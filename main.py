
import requests
import time
from lxml import html
import os
import json
from tqdm import tqdm

# username = "BeautifulFiction"
# r = requests.get("https://archiveofourown.org/users/" + username)
# tree = html.fromstring(r.text)

# fandoms = tree.xpath("//div[@id='user-fandoms']//a/@href")
# fandoms = [f.split("fandom_id=")[1] for f in fandoms]
# time.sleep(1)


def get_num_pages(tree):
    '''Finds out how many pages there are'''
    pages = tree.xpath("//ol[@title='pagination']/li//text()")
    max_page = 0
    for page in pages:
        try:
            page = int(page)
            max_page = max(max_page, page)
        except:
            pass
    return max_page

try:
    os.mkdir("fanfictions")
except FileExistsError:
    pass
# Get authors writing in fandom
# fandoms = [
#     "Marvel",
#     "Harry Potter - J*d* K*d* Rowling",
#     "Star Wars - All Media Types",
#     "Sherlock Holmes *a* Related Fandoms",
#     "TOLKIEN J*d* R*d* R*d* - Works *a* Related Fandoms"
# ]
relationships = [
    "Sherlock Holmes/John Watson",
    "Draco Malfoy/Harry Potter",
    "Steve Rogers/Tony Stark",
    "Castiel/Dean Winchester"
]


def request_till_200(url):
    '''Make a request till response is 200'''
    while True:
        r = requests.get(url)
        time.sleep(1)
        if r.status_code == 200 or r.status_code == 404:
            return r

        time.sleep(10)



for fandom in relationships:
    try:
        os.mkdir(os.path.join("fanfictions", fandom.replace("/", "*s*")))
    except FileExistsError:
        pass
    authors = []
    for page in range(1, 25):
        r = request_till_200("https://archiveofourown.org/tags/" + fandom.replace("/", "*s*") + "/works?page=" + str(page))



        # params = {
        #     "utf8": "✓",
        #     "work_search[single_chapter]": 0,
        #     "work_search[relationship_names]": fandom,
        #     "work_search[language_id]": "en"
        # }
        # r = requests.get("https://archiveofourown.org/works/search", params=params)

        tree = html.fromstring(r.text)
        page_authors = tree.xpath("//a[@rel='author']/@href")
        page_authors = [p.split("/")[-1] for p in page_authors]
        authors += page_authors

    # Get list of works for each user
    for username in tqdm(authors, desc=fandom, position=0):
        page = 1
        max_page = 2
        works = []
        while page < max_page:
            r = request_till_200("https://archiveofourown.org/users/" + username + "/works?page=" + str(page))
            tree = html.fromstring(r.text)
            max_page = get_num_pages(tree)
            page_works = tree.xpath("//h4[@class='heading']/a/@href")
            page_works = [w.split("/")[-1] for w in page_works if w.startswith("/works/")]
            # ratings = tree.xpath("//span[contains(@class, 'rating')]/@title")
            works += page_works
            page += 1


        # Get work text and metadata
        for fic_id in tqdm(works, desc=username, position=1, leave=False):
            url = 'http://archiveofourown.org/works/'+str(fic_id)+'?view_adult=true'
            url += '&amp;view_full_work=true'
            r = request_till_200(url)
            tree = html.fromstring(r.text)
            text_ps = tree.xpath("//div[@id='chapters']//p/text()")
            text_ps = [p.strip() for p in text_ps]
            text = "\n".join(text_ps).strip()

            def unpack_if_single(l):
                if len(l) == 1:
                    return l[0]
                return l

            summary_ps = tree.xpath("//div[@class='summary module']//blockquote//text()")
            summary_ps = [p.strip() for p in summary_ps]
            summary = "\n".join(summary_ps).strip()
            metadata = {
                "author": username,
                "summary": summary,
                "url": url,
                "title": tree.xpath("//h2[@class='title heading']//text()")[0].strip(),
                "fandoms": unpack_if_single(tree.xpath("///dd[@class='fandom tags']//a//text()")),
                "category": unpack_if_single(tree.xpath("///dd[@class='category tags']//a//text()")),
                "relationship": unpack_if_single(tree.xpath("///dd[@class='relationship tags']//a//text()")),
                "rating": unpack_if_single(tree.xpath("///dd[@class='rating tags']//a//text()")),
                "warning": unpack_if_single(tree.xpath("///dd[@class='warning tags']//a//text()")),
                "characters": unpack_if_single(tree.xpath("///dd[@class='character tags']//a//text()")),
                "language": tree.xpath("///dd[@class='language']//text()")[0].strip(),
            }
            if isinstance(metadata["relationship"], str) and metadata["relationship"] == fandom and metadata["language"] == "English":

                import hashlib
                doc_id = hashlib.sha1(text.encode("utf-8")).hexdigest()
                base_dir = os.path.join("fanfictions", fandom.replace("/","*s*"), username)
                try:
                    os.mkdir(base_dir)
                except Exception as e:
                    pass
                open(os.path.join(base_dir, doc_id + ".txt"), 'w').write(text)
                json.dump(metadata, open(os.path.join(base_dir, doc_id + ".json"), 'w'), indent=2)


        # Save works and metadata
        # Equal number of paragraphs from each fandom

        # Construct dataset
        # Num authors
        # Structure
        # Length
        # Pick paragraphs

