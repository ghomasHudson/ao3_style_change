# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import hashlib
import os
import json


class Ao3Pipeline:
    def process_item(self, item, spider):
        return item

class TreeStructure:
    def process_item(self, item, spider):
        # Make main dir
        try:
            os.mkdir("fanfictions")
        except FileExistsError:
            pass

        # Make relationship subdir
        base_dir = os.path.join("fanfictions", item["relationship"].replace("/", "*s*"))
        try:
            os.mkdir(base_dir)
        except FileExistsError:
            pass

        # Make author subdir
        base_dir = os.path.join(base_dir, item["author"])
        try:
            os.mkdir(base_dir)
        except FileExistsError:
            pass

        # Save item
        open(os.path.join(base_dir, item["work_id"] + ".txt"), 'w').write(item["full_text"])
        del item["full_text"]
        json.dump(item, open(os.path.join(base_dir, item["work_id"] + ".json"), 'w'), indent=2)
