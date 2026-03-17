import json
import os
import re
import shutil
import time
from pathlib import Path


with open("tag_folders.json", encoding="utf-8") as f:
    data = json.load(f)

tag_map = data["tags"]
ignore = set(data["ignore"])

# TODO sift through each note
SOURCE = Path(r"C:\Users\Eem\Dropbox\Accounting Notes")


PATTERN = re.compile(r"---\ntype:\s(\w+)\n")


for dirpath, subdirs, files in os.walk(SOURCE):
    for filename in files:
        if filename.endswith(".md"):
            file = os.path.join(dirpath, filename)
            with open(file, encoding="utf-8") as f:
                content = f.read()

            if match := PATTERN.match(content):
                tag = match.group(1)
                basename = os.path.basename(dirpath)

                # check if file is located in the correct dir
                if tag not in ignore:
                    if tag_map[tag] != basename and basename != "99 Templates":
                        shutil.move(file, SOURCE / basename)
                        print(f"{file} → {repr(SOURCE / tag_map[tag])}")


# TODO: scan in background, move new files if they need moving. 

