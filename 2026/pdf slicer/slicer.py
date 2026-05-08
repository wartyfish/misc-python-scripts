"""
slicer.py
---------
Auto-detects the grid layout of each page in a PDF and saves each cell
as an image. No manual measurement needed.

Usage:
    python slicer.py input.pdf
    python slicer.py input.pdf --output my_folder --dpi 300 --format JPEG

Requirements:
    pip install pymupdf Pillow numpy
"""

import argparse
import sys
from pathlib import Path

try:
    import fitz
except ImportError:
    sys.exit("Could not import 'fitz'. Try: pip install --upgrade pymupdf")
try:
    from PIL import Image
except ImportError:
    sys.exit("Missing dependency: pip install Pillow")
try:
    import numpy as np
except ImportError:
    sys.exit("Missing dependency: pip install numpy")


# ---------------------------------------------------------------------------
# Grid detection helpers
# ---------------------------------------------------------------------------

def find_white_bands(arr, x1, x2, y_start, y_end, threshold=0.95, min_size=5):
    """Return (start, end, size) tuples for near-white horizontal bands."""
    bands = []; in_w = False; start = 0
    for y in range(y_start, y_end):
        pct = (arr[y, x1:x2, :] >= 250).all(axis=1).mean()
        if pct >= threshold and not in_w:
            start = y; in_w = True
        elif pct < threshold and in_w:
            if y - start >= min_size:
                bands.append((start, y - 1, y - start))
            in_w = False
    return bands


def merge_close_gaps(gaps, max_dist=20):
    """Merge gap pairs separated by ≤ max_dist pixels (handles double-borders)."""
    if not gaps:
        return gaps
    merged = [gaps[0]]
    for s, e, sz in gaps[1:]:
        ps, pe, _ = merged[-1]
        if s - pe - 1 <= max_dist:
            merged[-1] = (ps, e, e - ps + 1)
        else:
            merged.append((s, e, sz))
    return merged


def scan_for_gaps(arr, y1, y2, x1, x2, axis,
                  threshold=0.95, min_gap=10, max_gap=150):
    """Return (start, end, size) white gaps along `axis` ('col' or 'row')."""
    region = arr[y1:y2, x1:x2]
    gaps = []; in_gap = False; start = 0
    length = region.shape[1] if axis == 'col' else region.shape[0]
    for i in range(length):
        strip = region[:, i, :] if axis == 'col' else region[i, :, :]
        pct = (strip >= 250).all(axis=1).mean()
        if pct >= threshold and not in_gap:
            start = i; in_gap = True
        elif pct < threshold and in_gap:
            sz = i - start
            off = x1 if axis == 'col' else y1
            if min_gap <= sz <= max_gap:
                gaps.append((start + off, i - 1 + off, sz))
            in_gap = False
    return gaps


def get_page_layout(arr):
    """
    Auto-detect cell boundaries for one page.
    Returns (col_ranges, row_ranges) as lists of (start, end) pixel pairs.

    Key design decisions:
    - grid_top: end of last near-white band in the top 40% of the page.
      Pages with a complex header (>3 bands) skip all header bands.
      Normal pages skip only the page border (1 band).
    - grid_right / grid_bot: inferred from cell size rather than relying on
      margin gaps, which are unreliable when image content is near-white.
    """
    h, w = arr.shape[:2]

    # --- grid top ---
    top_bands = find_white_bands(arr, 100, w - 100, 0, int(h * 0.4), min_size=5)
    if len(top_bands) > 3:
        grid_top = top_bands[-1][1] + 1   # complex header page
    elif top_bands and top_bands[0][0] <= 5:
        grid_top = top_bands[0][1] + 1    # normal page border
    else:
        grid_top = 0

    # --- approximate grid_bot (used only to bound gap scans) ---
    grid_bot_approx = h - 1
    for y in range(h - 1, grid_top, -1):
        if (arr[y, 200:w - 200, :] >= 250).all(axis=1).mean() < 0.95:
            grid_bot_approx = y
            break

    # --- columns ---
    # Scan a 300px-tall band at 1/3 height for vertical white gaps.
    mid_y1 = grid_top + (grid_bot_approx - grid_top) // 3
    mid_y2 = min(mid_y1 + 300, grid_bot_approx)
    all_col_gaps = scan_for_gaps(arr, mid_y1, mid_y2, 0, w, 'col')

    left_margins = [(s, e, sz) for s, e, sz in all_col_gaps if s < 200]
    col_dividers = [(s, e, sz) for s, e, sz in all_col_gaps if 200 <= s <= w - 200]

    grid_left = left_margins[-1][1] + 1 if left_margins else 0

    # Infer grid_right from cell width (more reliable than right-margin gap detection,
    # which fails when near-white image content extends to the page edge).
    if col_dividers:
        cell_w    = col_dividers[0][0] - grid_left
        grid_right = col_dividers[-1][1] + cell_w
    else:
        # Single-column fallback: scan backwards for last content pixel.
        grid_right = grid_left
        for x in range(w - 1, grid_left, -1):
            if (arr[mid_y1:mid_y2, x, :] >= 250).all(axis=1).mean() < 0.95:
                grid_right = x
                break

    # --- rows ---
    # Scan within the first column — reliably populated even on partial last pages.
    row_x1 = grid_left + 50
    row_x2 = grid_left + 500
    all_row_gaps = scan_for_gaps(arr, grid_top, grid_bot_approx, row_x1, row_x2, 'row')
    row_dividers = merge_close_gaps(
        [(s, e, sz) for s, e, sz in all_row_gaps if sz >= 20]
    )

    # Infer grid_bot from cell height (same reasoning as grid_right).
    if row_dividers:
        cell_h   = row_dividers[0][0] - grid_top
        grid_bot = row_dividers[-1][1] + cell_h
    else:
        grid_bot = grid_bot_approx

    # Build boundary lists
    col_starts = [grid_left] + [e + 1 for s, e, sz in col_dividers]
    col_ends   = [s - 1       for s, e, sz in col_dividers] + [grid_right]
    row_starts = [grid_top]  + [e + 1 for s, e, sz in row_dividers]
    row_ends   = [s - 1       for s, e, sz in row_dividers] + [grid_bot]

    return list(zip(col_starts, col_ends)), list(zip(row_starts, row_ends))


# ---------------------------------------------------------------------------
# Main extraction
# ---------------------------------------------------------------------------

def extract_grid(pdf_path, output_dir="output_images", dpi=300, image_format="PNG"):
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    pdf  = fitz.open(pdf_path)
    ext  = image_format.lower()
    zoom = dpi / 72
    total_saved = 0

    for page_num, page in enumerate(pdf, start=1):
        mat = fitz.Matrix(zoom, zoom)
        pix = page.get_pixmap(matrix=mat, alpha=False)
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        arr = np.array(img)

        col_ranges, row_ranges = get_page_layout(arr)
        n_cols, n_rows = len(col_ranges), len(row_ranges)

        print(f"Page {page_num}: detected {n_cols}×{n_rows} grid "
              f"({pix.width}×{pix.height}px)")

        for ri, (y1, y2) in enumerate(row_ranges, start=1):
            for ci, (x1, x2) in enumerate(col_ranges, start=1):
                cell_img = img.crop((x1, y1, x2, y2))
                fname = out / f"page{page_num:03d}_row{ri:02d}_col{ci:02d}.{ext}"
                cell_img.save(fname)
                total_saved += 1

    pdf.close()
    print(f"\nDone! {total_saved} images saved to '{out}/'")


def main():
    parser = argparse.ArgumentParser(
        description="Auto-detect and slice a PDF grid into individual cell images."
    )
    parser.add_argument("pdf",           help="Path to the input PDF")
    parser.add_argument("--output",      default="output_images",
                        help="Output directory (default: output_images)")
    parser.add_argument("--dpi",         type=int, default=300,
                        help="Render resolution in DPI (default: 300)")
    parser.add_argument("--format",      default="PNG",
                        choices=["PNG", "JPEG", "TIFF"],
                        help="Output image format (default: PNG)")
    args = parser.parse_args()

    extract_grid(
        pdf_path=args.pdf,
        output_dir=args.output,
        dpi=args.dpi,
        image_format=args.format,
    )


if __name__ == "__main__":
    main()