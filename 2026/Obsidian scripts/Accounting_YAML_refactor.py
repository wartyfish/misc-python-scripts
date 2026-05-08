#!/usr/bin/env python3
"""
Refactors Obsidian note frontmatter: converts 'module' field
from a single inline value to a YAML bullet point list.

Before:  module: "[[2.1.01 Business Documentation]]"
After:   module:
           - "[[2.1.01 Business Documentation]]"

Safe to re-run — skips files already in the correct format.
"""

import re
from pathlib import Path

VAULT_PATH = r"C:\Users\Eem\Dropbox\Accounting Notes"

# Matches the full frontmatter block
FRONTMATTER_RE = re.compile(r'\A(---\n)(.*?)(^---\s*$)', re.DOTALL | re.MULTILINE)


def refactor_frontmatter(fm: str) -> tuple[str, bool]:
    """
    Parse frontmatter line by line and convert the module field if needed.
    Returns (new_frontmatter, was_changed).
    """
    lines = fm.split('\n')
    new_lines = []
    changed = False
    i = 0

    while i < len(lines):
        line = lines[i]

        m = re.match(r'^(module:)(.*)', line)
        if m:
            value_part = m.group(2)
            value_stripped = value_part.strip()

            # Already a block list — "module:" with nothing after it
            if value_stripped == '':
                new_lines.append(line)
                i += 1
                continue

            # Already a bullet on the same line (guard)
            if value_stripped.startswith('- '):
                new_lines.append(line)
                i += 1
                continue

            # Inline value — convert to block list
            new_lines.append(f"module:")
            new_lines.append(f"  - {value_stripped}")
            changed = True
            i += 1
            continue

        new_lines.append(line)
        i += 1

    return '\n'.join(new_lines), changed


def process_file(filepath: Path, vault: Path) -> bool:
    """Process a single file. Returns True if the file was modified."""
    original = filepath.read_text(encoding='utf-8')

    match = FRONTMATTER_RE.match(original)
    if not match:
        return False  # No frontmatter

    open_fence = match.group(1)   # "---\n"
    frontmatter = match.group(2)  # content between the fences
    rest = original[match.end():]  # everything after closing ---
    close_fence = match.group(3)  # "---"

    new_frontmatter, changed = refactor_frontmatter(frontmatter)

    if not changed:
        return False

    new_content = open_fence + new_frontmatter + close_fence + rest
    filepath.write_text(new_content, encoding='utf-8')
    print(f"  ✅  Updated: {filepath.relative_to(vault)}")
    return True


def process_vault(vault_path: str) -> None:
    vault = Path(vault_path)
    if not vault.exists():
        print(f"❌  Vault not found: {vault_path}")
        return

    md_files = list(vault.rglob("*.md"))
    print(f"Found {len(md_files)} markdown files.\n")

    changed, skipped, errors = 0, 0, 0

    for filepath in md_files:
        try:
            if process_file(filepath, vault):
                changed += 1
            else:
                skipped += 1
        except Exception as exc:
            print(f"  ⚠️  Error: {filepath.name} — {exc}")
            errors += 1

    print(f"\n{'='*55}")
    print(f"  Done!  Changed: {changed}  |  Skipped: {skipped}  |  Errors: {errors}")
    print(f"{'='*55}")


if __name__ == "__main__":
    process_vault(VAULT_PATH)