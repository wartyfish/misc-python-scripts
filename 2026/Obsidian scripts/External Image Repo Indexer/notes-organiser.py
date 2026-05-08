import json
import os
import re
import shutil
import time
import yaml
from image_repo_indexer import build_image_gallery
from pathlib import Path

PATTERN = re.compile(r"---\ntype:\s([\w/-]+)\n")

def load_type_map(map_note_path: str) -> dict:
    with open(map_note_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Extract content between the yaml fences
    _, _, rest = content.partition("---\n")
    yaml_str, _, _, = rest.partition("---")

    return yaml.safe_load(yaml_str)

def process_notes(vault: Path, tag_map: dict, source: Path=None, ignore: set=None, cooldown=5):
    """Scan markdown files and move them if needed."""
    if not source:
        source = vault

    now = time.time()

    for dirpath, _, files in os.walk(source):
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

            if ignore and tag in ignore:
                continue

            target_folder = vault / tag_map.get(tag, basename)

            if basename != "99 Templates" and basename != target_folder.name:
                target_path = target_folder / filename
                target_folder.mkdir(parents = True, exist_ok=True)

                shutil.move(str(file_path), str(target_path))
                print(f"{file_path.name} → {target_path.relative_to(vault.parent)}")

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

def get_dir_state(path: Path):
    files = [f for f in path.rglob("*") if f.is_file()]
    if not files:
        return (0, 0)
    return (len(files), max(f.stat().st_mtime for f in files))

def watch_folder(vault: Path, tag_map: dict, source: Path=None, ignore: set=None, interval: int=1, cooldown: int=5):
    """Watch folder and only process files that haven't changed for 'cooldown' seconds."""
    last_mtime = get_latest_mtime(vault)

    while True:
        time.sleep(interval)

        current_mtime = get_latest_mtime(vault)

        if current_mtime != last_mtime:
            process_notes(vault, tag_map, source, ignore)
            last_mtime = current_mtime

def watch_paths(watchers: list[dict], interval: int=1):
    """
    Watch multiple paths for new files, each with its own handler.
    watchers: list of dicts with keys 'path' and 'handler'
    """
    for w in watchers:
        w["last_state"] = w["state_fn"](w["path"])

    while True:
        time.sleep(interval)
        for w in watchers:
            current_state = w["state_fn"](w["path"])
            if current_state != w["last_state"]:
                w["handler"]()
                w["last_state"] = current_state

if __name__ == "__main__":
    VAULT_PATH = Path(r"C:\Users\Eem\Dropbox\Jamies Vault")
    TIEDYE_PROJECT_IMAGES_REPO = Path(r"P:\Photos\Tie Dye")
    TIEDYE_NOTE_PATH = Path(r"C:\Users\Eem\Dropbox\Jamies Vault\03 Projects\Tie Dye\Project Images.md")
    TIEDYE_THUMBNAIL_WIDTH = 500
    INSPO_REPO = Path(r"P:\Obsidian vault backups\_Vault Image Repo\Tie Dye Inspo Images")
    INSPO_NOTE_PATH = Path(r"C:\Users\Eem\Dropbox\Jamies Vault\03 Projects\Tie Dye\Image Index.md")
    INSPO_THUMNAIL_WIDTH = 500
    MAP_NOTE_PATH = VAULT_PATH / "02 Docs" / "Note Folder Map.md"

    type_map = load_type_map(MAP_NOTE_PATH)
    inbox = VAULT_PATH / "00 Inbox"

    watchers = [
        {
            "path": VAULT_PATH,
            "state_fn": get_latest_mtime,
            "handler": lambda: process_notes(VAULT_PATH, type_map, inbox)
        },
        {
            "path": INSPO_REPO,
            "state_fn": get_dir_state,
            "handler": lambda: build_image_gallery(INSPO_REPO, INSPO_NOTE_PATH, INSPO_THUMNAIL_WIDTH)
        },
        {
            "path": TIEDYE_PROJECT_IMAGES_REPO,
            "state_fn": get_dir_state,
            "handler": lambda: build_image_gallery(TIEDYE_PROJECT_IMAGES_REPO, TIEDYE_NOTE_PATH, TIEDYE_THUMBNAIL_WIDTH)
        }
    ]

    process_notes(VAULT_PATH, type_map, inbox)    

    print(f"Watching {VAULT_PATH} and {INSPO_REPO}...")
    try:
        watch_paths(watchers)
    except KeyboardInterrupt:
        pass

    