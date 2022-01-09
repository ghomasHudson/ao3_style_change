"""AO3 style change detection"""

import csv
import json
import os
import glob

import datasets


_CITATION = """\
"""

_DESCRIPTION = """\
Style change detection is the task of identifying the points where the author changes in a document constructed from the work of multiple authors.

This dataset is based on the fanfiction website AO3 and is designed to test the ability of models to solve style change detection on long documents (>10,000 tokens).
"""

_HOMEPAGE = "https://github.com/ghomasHudson/ao3_style_change"

_LICENSE = ""

_URL = "https://github.com/ghomasHudson/ao3_style_change/archive/master.zip"

class AO3StyleChange(datasets.GeneratorBasedBuilder):
    """AO3 Style Change: Detecting author changes in multiauthored documents."""

    VERSION = datasets.Version("1.1.0")

    def _info(self):
        return datasets.DatasetInfo(
            description=_DESCRIPTION,
            features = datasets.Features(
                {
                    "site": datasets.Value("string"),
                    "authors": datasets.Value("int32"),
                    "structure": datasets.features.Sequence(
                        datasets.Value("string")
                    ),
                    "multi-author": datasets.Value("bool"),
                    "changes": datasets.features.Sequence(
                        datasets.Value("bool")
                    ),
                    "paragraph-authors": datasets.features.Sequence(
                        datasets.Value("int32")
                    ),
                    "paragraphs": datasets.features.Sequence(
                        datasets.Value("string")
                    )

                }
            ),
            homepage=_HOMEPAGE,
            license=_LICENSE,
            citation=_CITATION,
        )

    def _split_generators(self, dl_manager):
        data_dir = dl_manager.download_and_extract(_URL)
        data_dir = os.path.join(data_dir, "ao3_style_change-master", "data")
        return [
            datasets.SplitGenerator(
                name=datasets.Split.TRAIN,
                gen_kwargs={
                    "split_data_dir": os.path.join(data_dir, "train"),
                },
            ),
            datasets.SplitGenerator(
                name=datasets.Split.TEST,
                gen_kwargs={
                    "split_data_dir": os.path.join(data_dir, "test"),
                },
            ),
            datasets.SplitGenerator(
                name=datasets.Split.VALIDATION,
                gen_kwargs={
                    "split_data_dir": os.path.join(data_dir, "validation"),
                },
            ),
        ]

    def _generate_examples(self, split_data_dir):
        for key, doc in enumerate(glob.glob(os.path.join(split_data_dir, "*.txt"))):
            text = open(doc).read().strip()
            metadata = json.load(open(doc[:-3].replace("problem-", "truth-problem-")+"json"))
            metadata["paragraphs"] = text.split("\n")
            assert len(metadata["paragraphs"]) == len(metadata["paragraph-authors"])
            yield key, metadata
