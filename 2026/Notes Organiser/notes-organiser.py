import json
import os
import re
import shutil
import time
from pathlib import Path

PATTERN = re.compile(r"---\ntype:\s(\w+)\n")



def process_notes(source: Path, tag_map: dict, ignore: set, cooldown=5):
    """Scan markdown files and move them if needed."""
    now = time.time()

    for dirpath, _, files in os.walk(SOURCE):
        for filename in files:
            if not filename.endswith(".md"):
                continue

            file_path = Path(dirpath) / filename

            try:
                mtime = file_path.stat().st_mtime
            except FileNotFoundError:
                continue

            # Skip files that were recently modified
            if now - mtime < cooldown:
                continue

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

def get_latest_mtime(path: Path):
    """Get latest modification time of all files in directory."""
    latest = 0
    for dirpath, _, files in os.walk(path):
        for f in files:
            full_path = os.path.join(dirpath, f)
            try:
                latest = max(latest, os.path.getmtime(full_path))
            except FileNotFoundError:
                pass
    return latest

def watch_folder(source: Path, tag_map: dict, ignore: set, interval=1, cooldown=5):
    """Watch folder and only process files that haven't changed for 'cooldown' seconds."""
    last_mtime = get_latest_mtime(source)

    while True:
        time.sleep(interval)

        current_mtime = get_latest_mtime(source)

        if current_mtime != last_mtime:
            print("Changes detected, processing...")
            process_notes(source, tag_map, ignore)
            last_mtime = current_mtime

if __name__ == "__main__":
    with open("tag_folders.json", encoding="utf-8") as f:
        data = json.load(f)

    tag_map = data["tags"]
    ignore = set(data["ignore"])

    SOURCE = Path(r"C:\Users\Eem\Dropbox\Accounting Notes")

    watch_folder(SOURCE, tag_map, ignore)