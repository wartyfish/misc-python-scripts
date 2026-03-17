import json
import os
import re
import shutil
import time
from pathlib import Path

PATTERN = re.compile(r"---\ntype:\s(\w+)\n")



def process_notes(source: Path, tag_map: dict, ignore: set):
    """Scan markdown files and move them if needed."""
    for dirpath, subdirs, files in os.walk(SOURCE):
        for filename in files:
            if not filename.endswith(".md"):
                continue

            file_path = Path(dirpath) / filename

            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            match = PATTERN.match(content)
            if not match:
                continue

            tag = match.group(1)
            basename = Path(dirpath).name

            if tag in ignore:
                continue

            target_folder = source / tag_map.get(tag, basename)

            if basename != "99 Templates" and basename != target_folder.name:
                target_path = target_folder / filename
                target_folder.mkdir(parents = True, exist_ok=True)

                shutil.move(str(file_path), str(target_path))
                print(f"{file_path.name} → {target_path.relative_to(SOURCE.parent)}")



# TODO: scan in background, move new files if they need moving. 
if __name__ == "__main__":
    with open("tag_folders.json", encoding="utf-8") as f:
        data = json.load(f)

    tag_map = data["tags"]
    ignore = set(data["ignore"])

    SOURCE = Path(r"C:\Users\Eem\Dropbox\Accounting Notes")

    process_notes(SOURCE, tag_map, ignore)