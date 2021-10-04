# ao3_style_change
Style change detection dataset using AO3 fics. Inspired by the [PAN 21: Style Change Detection Task](https://pan.webis.de/clef21/pan21-web/style-change-detection.html).

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
