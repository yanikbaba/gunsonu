#!/usr/bin/env python3
"""
Update Notifier (v0.8.1)
- Compares local VERSION with optional latest version file path/URL argument
- If no source provided, prints noop message (integrate later with online check)
Usage:
    python src/tools/update_notifier.py --current 0.8.1 --latest-file RELEASE_LATEST.json
"""
import argparse, json, os, sys

def parse_ver(s): 
    return tuple(int(x) for x in s.strip("v").split("."))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--current', default='0.8.1')
    ap.add_argument('--latest-file', default=None)
    args = ap.parse_args()
    cur = parse_ver(args.current)
    lat = cur
    if args.latest_file and os.path.exists(args.latest_file):
        with open(args.latest_file,'r',encoding='utf-8') as f:
            lat = parse_ver(json.load(f).get("latest","0.0.0"))
    if lat > cur:
        print(f"[update] New version available: v{'.'.join(map(str,lat))}")
        sys.exit(10)
    else:
        print("[update] Up to date.")
        sys.exit(0)

if __name__ == "__main__":
    main()
