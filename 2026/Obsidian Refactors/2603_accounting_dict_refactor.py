import re
import sys
from pathlib import Path


def convert_note(content: str) -> tuple[str, bool]:
    """
    Convert a Format 1 atom note to Format 2.
    Returns (converted_content, was_changed).
    """

    # Split frontmatter from body
    fm_match = re.match(r'^---\n(.*?)\n---\n(.*)', content, re.DOTALL)
    if not fm_match:
        return content, False

    frontmatter = fm_match.group(1)
    body = fm_match.group(2)

    # Find the definition line in the body:
    # Matches: **Title:** Definition text ^def
    def_match = re.search(
        r'^\*\*[^*]+\*\*:\s*(.+?)\s*\^def\s*$',
        body,
        re.MULTILINE
    )

    if not def_match:
        return content, False

    definition = def_match.group(1).strip()
    full_def_line = def_match.group(0)

    # Inject definition into frontmatter, before the tags: line
    if 'definition:' in frontmatter:
        # Already has a definition field — overwrite it
        frontmatter = re.sub(
            r'definition:.*',
            f'definition: "{definition}"',
            frontmatter
        )
    else:
        # Insert before tags:
        frontmatter = re.sub(
            r'(tags:)',
            f'definition: "{definition}"\n\\1',
            frontmatter
        )

    # Remove the definition line from the body
    body = body.replace(full_def_line, '').strip()

    # Clean up any double blank lines left behind
    body = re.sub(r'\n{3,}', '\n\n', body)

    new_content = f"---\n{frontmatter}\n---\n{body}\n"
    return new_content, True


def process_file(path: Path, dry_run: bool = False) -> bool:
    content = path.read_text(encoding='utf-8')
    new_content, changed = convert_note(content)

    if not changed:
        print(f"  [SKIP] No ^def found:     {path.name}")
        return False

    if dry_run:
        print(f"  [DRY RUN] Would convert:  {path.name}")
        print("-" * 60)
        print(new_content)
        print("-" * 60)
    else:
        path.write_text(new_content, encoding='utf-8')
        print(f"  [OK] Converted:           {path.name}")

    return True


def main():
    args = sys.argv[1:]

    if not args:
        print("Usage:")
        print("  python convert_atoms.py <file.md>              # convert single file")
        print("  python convert_atoms.py <folder/>              # convert all .md in folder")
        print("  python convert_atoms.py <file.md> --dry-run    # preview without saving")
        print("  python convert_atoms.py <folder/> --dry-run    # preview folder")
        sys.exit(0)

    dry_run = '--dry-run' in args
    targets = [a for a in args if not a.startswith('--')]

    converted = 0
    skipped = 0

    for target in targets:
        path = Path(target)

        if path.is_file():
            result = process_file(path, dry_run)
            if result:
                converted += 1
            else:
                skipped += 1

        elif path.is_dir():
            files = sorted(path.rglob('*.md'))
            print(f"\nScanning {len(files)} .md files in '{path}'...\n")
            for f in files:
                result = process_file(f, dry_run)
                if result:
                    converted += 1
                else:
                    skipped += 1
        else:
            print(f"  [ERROR] Path not found: {target}")

    print(f"\nDone. Converted: {converted} | Skipped: {skipped}")


if __name__ == '__main__':
    main()