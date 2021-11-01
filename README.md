# AO3 Style Change Detection
Style change detection dataset using AO3 fics. Inspired by the [PAN 21: Style Change Detection Task](https://pan.webis.de/clef21/pan21-web/style-change-detection.html), but for much longer documents.

# Dataset construction methodology
We pick 4 relationships from different popular fandoms on AO3:
- Sherlock Holmes/John Watson
- Castiels/Dean Winchester
- Steve Rodgers/Tony Stark
- Draco Malfoy/Harry Potter

For each pairing, we find collect stories which include it, and are written in English. We collate these by author and randomly generate documents which contain paragraphs from 1-3 authors.

# Data Format

We use the same data format as the [PAN 21](https://pan.webis.de/clef21/pan21-web/style-change-detection.html) task, with 2 files for each problem instance, `x`:
- `problem-x.txt` containing the text
- `truth-problem-x.json` containing the ground truth (labels), e.g.
```json
{
    "site": "Sherlock Holmes/John Watson",
    "authors": 3,
    "multiauthor": 1,
    "structure": ["Username1", "Username2", "Username1", "Username3"],
    "changes": [0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, ...],
    "paragraph-authors": [1, 1, 1, 1, 1, 2, 2, 2, 2, ...]
}
```


# Gathering new data

2 python files are provided which were used when scraping the data:
- `main.py` iterates through the list of character pairings, downloading fics in the following structure:
```
fanfics/
├── pairing1
│   ├── Username1
│   │    ├── 3b6ff2cadcaedf11d5eaaefd1e998d49c493c45f.json
│   │    ├── 3b6ff2cadcaedf11d5eaaefd1e998d49c493c45f.txt
│   │    ├── ab35ee7ceb06ee97c94cd042d8874f1eab99bd1a.json
│   │    ├── ab35ee7ceb06ee97c94cd042d8874f1eab99bd1a.txt
│   │    └── ...
│   ├── Username2
│   │    └── ...
│   ...
└── pairing2
│   ├── Username3
│   │    └── ...
│   ├── Username4
│   │    └── ...
    ...
```
- `to_style_change.py` turns this into a style change task, by randomly creating a structure and filling it with random paragraphs.

# Baseline model (WIP)
`run_baseline.sh` will train a simple baseline model based on chunking the data.
