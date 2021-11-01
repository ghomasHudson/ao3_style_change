'''Convert downloaded fics into a style-change detection dataset'''

import os
import glob
import json
import random
import numpy as np

from utils import MyEncoder, NoIndent

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
NUM_PER_SET = 999999
random.seed(42)
np.random.seed(42)
# BUFFER = 1000
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

    for dataset_idx in range(NUM_PER_SET):
        if len(post_map) == 0:
            raise Exception("No more authors left")

        length = random.randint(10000, 30000)
        if random.random() <= 0.5:
            num_authors = 1
        else:
            num_authors = random.randint(2, 4)

        if num_authors == 1:

            # Find author with enough length
            new_author = None
            available_len = -1
            while available_len < length:
                new_author = random.sample(list(post_map.keys()), 1)[0]
                available_len = len(" ".join(post_map[new_author]).split()) * 0.8
            author_id = new_author

            post_map[author_id] = random.sample(post_map[author_id], len(post_map[author_id]))

            # Randomly pick paras
            paras = []
            while len("".join(paras).split()) < length:
                try:
                    section_paras.append(post_map[author_id].pop())
                except Exception as e:
                    # curr_len = len("".join(section_paras).split())
                    # orig_available_len = len(" ".join(post_map[author_ids[section-1]]).split())
                    reject = True
                    break
                    # print(e)
                    # breakpoint()
            labels = {
                "site": fandom.replace("*s*", "/"),
                "authors": 1,
                "structure": NoIndent([author_id]),
                "multi-author": 0,
                "changes": NoIndent([0] * len(paras)),
                "paragraph-authors": NoIndent([1] * len(paras))
            }

        else:
            num_switches = random.randint(num_authors-1,10)

            structure = createMixSenario(num_authors-1, num_switches)

            # Work out how long each section should be
            lengths = (np.random.dirichlet(np.ones(num_switches+1),size=1) * length)
            lengths = list(lengths[0])

            # Find length needed per author idx (e.g. author 1 needs 600 words...)
            author_length_map = {}
            for i in range(len(lengths)):
                author_length_map[structure[i]] = int(author_length_map.get(structure[i], 0) + lengths[i])

            # Pick authors
            author_ids = []
            paras_to_pick = {}
            for i in set(structure):
                new_author = None
                available_len = -1
                while new_author in author_ids or available_len < author_length_map[i]:
                    new_author = random.sample(list(post_map.keys()), 1)[0]
                    available_len = len(" ".join(post_map[new_author]).split()) * 0.8
                author_ids.append(new_author)

            # Shuffle
            for author_id in author_ids:
                post_map[author_id] = random.sample(post_map[author_id], len(post_map[author_id]))

            # Construct document
            reject = False
            paras = []
            for i in range(len(structure)):
                section = structure[i]
                section_paras = []
                while len("".join(section_paras).split()) < lengths[i]:
                    try:
                        section_paras.append(post_map[author_ids[section-1]].pop())
                    except Exception as e:
                        curr_len = len("".join(section_paras).split())
                        orig_available_len = len(" ".join(post_map[author_ids[section-1]]).split())
                        reject = True
                        break
                        # print(e)
                        # breakpoint()
                paras.append(section_paras)

            if reject:
                continue

            # Cleanup post_map
            post_map = {k:v for (k,v) in post_map.items() if len(v) > 0}
            # Output
            paragraph_authors = make_paragraph_author_list(paras, structure)

            labels = {
                "site": fandom.replace("*s*", "/"),
                "authors": num_authors,
                "structure": NoIndent([author_ids[s-1] for s in structure]),
                "multi-author": int(num_authors!=1),
                "changes": NoIndent(make_changes_list(paragraph_authors)),
                "paragraph-authors": NoIndent(paragraph_authors)
            }

        base_dir = os.path.join("style_change", fandom)
        with open(os.path.join(base_dir, 'truth-problem-'+str(dataset_idx+1)+'.json'), 'w') as fp:
            fp.write(json.dumps(labels, cls=MyEncoder, sort_keys=False, indent=2))
        with open(os.path.join(base_dir, "problem-"+str(dataset_idx+1)+".txt"), 'w') as f:
            for section in paras:
                for para in section:
                    f.write(para.strip() + "\n")
