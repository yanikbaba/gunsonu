#!/usr/bin/env python3
"""
Crash Snapshot Sanitizer (v0.8.1)
- Reads text-like crash files from input directory
- Scrubs PII (emails, phones, Windows paths, usernames)
- Hashes sensitive tokens with SHA256(salt) and keeps last 6 chars for correlation
- Writes sanitized copies to output directory, preserving filenames
Usage:
    python src/tools/crash_sanitize.py --in reports/crash --out reports/crash_sanitized --salt "GunSonuSalt"
"""
import argparse, os, re, hashlib, time, pathlib

EMAIL = re.compile(r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}')
PHONE = re.compile(r'(?:(?:\+?\d{1,3})?[ -]?)?(?:\(?\d{3}\)?[ -]?)?\d{3}[ -]?\d{2,4}')
WPATH = re.compile(r'[A-Za-z]:\\(?:[^\\\r\n]+\\)*[^\\\r\n]*')
USER  = re.compile(r'(?<=User: )[A-Za-z0-9_.-]+', re.IGNORECASE)

def mask(token: str, salt: str) -> str:
    h = hashlib.sha256((salt + token).encode('utf-8')).hexdigest()
    return f"<HASH:{h[-6:]}>"
    
def scrub(text: str, salt: str) -> str:
    text = EMAIL.sub(lambda m: mask(m.group(0), salt), text)
    text = PHONE.sub(lambda m: mask(m.group(0), salt), text)
    text = WPATH.sub(lambda m: "<PATH>", text)
    text = USER.sub(lambda m: "User:<HASH:"+hashlib.sha256((salt+m.group(0)).encode('utf-8')).hexdigest()[-6:]+">", text)
    # Normalize timestamps like 2025-10-31 15:22:33 -> 2025-10-31T15:22Z (approx)
    text = re.sub(r'(\d{4})-(\d{2})-(\d{2})[ T](\d{2}):(\d{2})(?::\d{2})?', r'\1-\2-\3T\4:\5Z', text)
    return text

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--in', dest='inp', default='reports/crash', help='input folder')
    ap.add_argument('--out', dest='out', default='reports/crash_sanitized', help='output folder')
    ap.add_argument('--salt', dest='salt', default='GunSonuSalt', help='hash salt')
    args = ap.parse_args()
    inp = pathlib.Path(args.inp); out = pathlib.Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    count = 0
    for p in inp.glob("**/*"):
        if p.is_file():
            try:
                text = p.read_text(errors='ignore')
            except Exception:
                continue
            clean = scrub(text, args.salt)
            dst = out / p.relative_to(inp)
            dst.parent.mkdir(parents=True, exist_ok=True)
            dst.write_text(clean, encoding='utf-8')
            count += 1
    print(f"[sanitizer] processed files: {count} -> {out}")
if __name__ == "__main__":
    main()
