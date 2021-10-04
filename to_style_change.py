'''Convert downloaded fics into a style-change detection dataset'''

import os
import glob
import json
import random

def make_changes_list(paragraph_authors):
    '''Turns a list of author idx per para into a list of changes'''
    out = []
    for i in range(1, len(paragraph_authors)):
        if paragraph_authors[i-1] == paragraph_authors[i]:
            out.append(0)
        else:
            out.append(1)
    return out

def make_paragraph_author_list(paras, structure):
    '''Make list of author idx per paragraph'''
    out = []
    for i, section in enumerate(paras):
        author_idx = structure[i]
        out += [author_idx] * len(section)
    return out

def createMixSenario(numAuthors: int, numSwitches:int):
    '''Returns a list of sections/authors (e.g. 1-2-3-2-2-1-3)'''
    mix = []
    for i in range(1, numAuthors+1):
        mix.append(i)

    usedSwitches = numAuthors - 1
    while usedSwitches < numSwitches:
        author = random.randint(0, numAuthors) + 1
        # search for first possible insert position such that the previous section is not from the same author
        for j in range(1, len(mix) + 1):
            previousAuthor = mix[j-1]
            if j == len(mix):
                nextAuthor = -1
            else:
                nextAuthor = mix[j]

            if previousAuthor != author and nextAuthor != author:
                mix.insert(j, author)
                usedSwitches += 1
                break
    return mix

try:
    os.mkdir("style_change")
except:
    raise Exception("Style change already exists")

#       Build map of fandom/author/paragraphs
NUM_PER_SET = 100
random.seed(42)
p_map = {}
for fandom_path in glob.glob("fanfictions/*"):
    fandom = fandom_path.split("/")[-1]
    os.mkdir(os.path.join("style_change", fandom))
    post_map = {}
    for author_path in glob.glob(fandom_path + "/*"):
        author = author_path.split("/")[-1]
        post_map[author] = []
        for doc in glob.glob(os.path.join(author_path, "*.txt")):
            text = open(doc).readlines()
            metadata = json.load(open(doc[:-3]+"json"))
            text = [t.strip() for t in text if len(t) > 5]
            post_map[author] += text

    for i in range(NUM_PER_SET):
        length = random.randint(10000, 30000)
        num_authors = random.randint(2, 3)
        num_switches = random.randint(num_authors-1,10)

        structure = createMixSenario(num_authors-1, num_switches)

        # Work out how long each section should be
        import numpy as np
        lengths = (np.random.dirichlet(np.ones(num_switches+1),size=1) * length)
        lengths = list(lengths[0])

        # Find length per author
        author_length_map = {}
        for i in range(len(lengths)):
            author_length_map[structure[i]] = int(author_length_map.get(structure[i], 0) + lengths[i])

        # Pick authors
        author_ids = []
        paras_to_pick = {}
        breakpoint()
        for i in set(structure):
            new_author = None
            available_len = -1
            while new_author in author_ids or available_len < author_length_map[i+1]:
                new_author = random.sample(list(post_map.keys()), 1)[0]
                available_len = len(" ".join(post_map[new_author]).split())
            author_ids.append(new_author)

        for author_id in author_ids:
            paras_to_pick[author_id] = random.sample(post_map[author_id], len(post_map[author_id]))

        # Construct document
        paras = []
        for i in range(len(structure)):
            section = structure[i]
            section_paras = []
            while len("".join(section_paras).split()) < lengths[i]:
                section_paras.append(paras_to_pick[author_ids[section-1]].pop())
            paras.append(section_paras)

        # Output
        paragraph_authors = make_paragraph_author_list(paras, structure)

        from utils import MyEncoder, NoIndent
        labels = {
            "site": fandom.replace("*s*", "/"),
            "authors": num_authors,
            "structure": NoIndent([author_ids[s-1] for s in structure]),
            "multi-author": int(num_authors!=1),
            "changes": NoIndent(make_changes_list(paragraph_authors)),
            "paragraph-authors": NoIndent(paragraph_authors)
        }
        base_dir = os.path.join("style_change", fandom)
        with open(os.path.join(base_dir, 'truth-problem-'+str(i+1)+'.json'), 'w') as fp:
            fp.write(json.dumps(labels, cls=MyEncoder, sort_keys=False, indent=2))
        with open(os.path.join(base_dir, "problem-"+str(i+1)+".txt"), 'w') as f:
            for section in paras:
                for para in section:
                    f.write(para.strip() + "\n")
