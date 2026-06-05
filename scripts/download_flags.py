#!/usr/bin/env python3
"""
One-time setup: download all WC 2026 team flags from flagcdn.com into docs/assets/flags/.
Run once locally (or in CI setup step) before the tournament starts.
Usage: python scripts/download_flags.py
"""

import os
import sys
import time
import requests
from flag_map import TLA_TO_ISO

FLAGS_DIR = os.path.join(os.path.dirname(__file__), "..", "docs", "assets", "flags")
CDN_URL   = "https://flagcdn.com/w320/{iso}.png"


def download_flag(iso: str, dest: str) -> bool:
    url = CDN_URL.format(iso=iso)
    try:
        resp = requests.get(url, timeout=15)
        if resp.status_code == 200 and resp.headers.get("content-type", "").startswith("image"):
            with open(dest, "wb") as fh:
                fh.write(resp.content)
            return True
        print(f"  SKIP {iso}: HTTP {resp.status_code}")
        return False
    except Exception as e:
        print(f"  ERROR {iso}: {e}")
        return False


def main():
    os.makedirs(FLAGS_DIR, exist_ok=True)

    # Collect unique ISO codes
    seen = set()
    to_download = []
    for tla, iso in TLA_TO_ISO.items():
        key = iso.upper()
        if key not in seen:
            seen.add(key)
            dest = os.path.join(FLAGS_DIR, f"{key}.png")
            to_download.append((iso, dest))

    total = len(to_download)
    print(f"Downloading {total} flags to {FLAGS_DIR}…")

    ok = skipped = failed = 0
    for i, (iso, dest) in enumerate(to_download, 1):
        fname = os.path.basename(dest)
        if os.path.exists(dest):
            print(f"  [{i}/{total}] {fname} already exists — skip")
            skipped += 1
            continue

        print(f"  [{i}/{total}] Downloading {fname}…", end=" ", flush=True)
        if download_flag(iso, dest):
            print("OK")
            ok += 1
        else:
            failed += 1
        time.sleep(0.15)  # polite pacing for CDN

    print(f"\nDone: {ok} downloaded, {skipped} skipped, {failed} failed.")
    if failed:
        sys.exit(1)


if __name__ == "__main__":
    main()
