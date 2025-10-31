#!/usr/bin/env python3
# GunSonu - Minimal PDF probe using fpdf2 (no warnings, ASCII-safe)

import argparse, os, sys, hashlib
from datetime import datetime

try:
    from fpdf import FPDF, XPos, YPos
except Exception as e:
    sys.stderr.write("fpdf2 import failed: %r\n" % (e,))
    sys.exit(4)

def build_pdf(path: str, pages: int) -> None:
    pdf = FPDF(orientation='P', unit='mm', format='A4')
    stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    filler = [
        "This is a deterministic smoke test line.",
        "GunSonu project: PDF module verification.",
        "Ascii-only content to avoid font encoding issues.",
        "CI pipeline artifact. Safe to delete.",
        "Data: project=GunSonu; module=PDF; test=smoke; version=1.0.",
    ]
    big_block = filler * 60  # ensures size > 8KB

    for i in range(1, pages+1):
        pdf.add_page()
        pdf.set_font('Helvetica', 'B', 16)
        pdf.cell(0, 10, 'GunSonu - PDF Smoke Test', new_x=XPos.LMARGIN, new_y=YPos.NEXT)

        pdf.set_font('Helvetica', '', 11)
        pdf.cell(0, 8, f"Page: {i}/{pages}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.cell(0, 8, f"Timestamp: {stamp}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.cell(0, 8, "Probe: fpdf2 A4 page", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.cell(0, 8, "Content: deterministic layout for CI smoke verification", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.cell(0, 8, "Fields: project=GunSonu; module=PDF; test=smoke", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

        pdf.set_font('Helvetica', '', 10)
        for ln in big_block:
            pdf.cell(0, 6, ln, new_x=XPos.LMARGIN, new_y=YPos.NEXT)

        pdf.set_font('Helvetica', 'I', 9)
        pdf.cell(0, 6, "(c) GunSonu Test Bot - Auto-generated for QA", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    pdf.output(path)

def sha256(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--pages", type=int, default=2)
    ap.add_argument("--min-bytes", type=int, default=8192)
    args = ap.parse_args()

    out = os.path.abspath(args.out)
    os.makedirs(os.path.dirname(out), exist_ok=True)

    try:
        build_pdf(out, max(1, args.pages))
    except Exception as e:
        sys.stderr.write(f"PDF generation failed: {e}\n")
        return 2

    size = os.path.getsize(out)
    digest = sha256(out)

    if size < args.min_bytes:
        sys.stderr.write(f"PDF too small: {size} bytes (< {args.min_bytes}).\n")
        return 2

    print(f"OK {out}")
    print(f"SIZE {size}")
    print(f"SHA256 {digest}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
