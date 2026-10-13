"""Render every page of PDFs to PNG images using PyMuPDF.

Usage:
    pip install pymupdf
    python pdf_to_images.py input.pdf [more.pdf | folder] -o out_dir --dpi 300 [--password PW]

Output: out_dir/<pdf_name>/page_0001.png ...
"""
import argparse
import sys
from pathlib import Path

import pymupdf as fitz


def collect(inputs):
    for p in map(Path, inputs):
        if p.is_dir():
            yield from sorted(p.rglob("*.pdf"))
        elif p.suffix.lower() == ".pdf":
            yield p


def render(pdf: Path, out_root: Path, dpi: int, password: str | None):
    doc = fitz.open(pdf)
    if doc.needs_pass and not doc.authenticate(password or ""):
        print(f"[skip] {pdf}: needs a password (use --password)", file=sys.stderr)
        return 0
    out = out_root / pdf.stem
    out.mkdir(parents=True, exist_ok=True)
    zoom = dpi / 72
    mat = fitz.Matrix(zoom, zoom)
    for i, page in enumerate(doc, start=1):
        page.get_pixmap(matrix=mat, alpha=False).save(out / f"page_{i:04d}.png")
    n = doc.page_count
    doc.close()
    print(f"[ok] {pdf} -> {out} ({n} pages)")
    return n


def main():
    ap = argparse.ArgumentParser(description="Convert PDF pages to PNG images")
    ap.add_argument("inputs", nargs="+", help="PDF files or folders")
    ap.add_argument("-o", "--out", default="images", help="output folder")
    ap.add_argument("--dpi", type=int, default=300)
    ap.add_argument("--password", default=None)
    a = ap.parse_args()
    total = sum(render(p, Path(a.out), a.dpi, a.password) for p in collect(a.inputs))
    print(f"Done: {total} pages")


if __name__ == "__main__":
    main()
