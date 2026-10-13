"""Download monthly Registr smluv (contract register) dumps from the official open-data site.

    python ingest/download_contracts.py 2026-07 2026-08 2026-09

Each month is one XML file of every contract record published that month (~120-140 MB).
Files already downloaded are skipped, so the script can be re-run after a dropped connection.
"""
import sys
import time
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "contracts"
URL = "https://data.smlouvy.gov.cz/dump_{y}_{m}.xml"


def download(month: str, attempts: int = 5):
    y, m = month.split("-")
    target = RAW / f"dump_{y}_{m}.xml"
    if target.exists() and target.stat().st_size > 0:
        print(f"{target.name}: already there")
        return
    tmp = target.with_suffix(".part")
    for attempt in range(1, attempts + 1):
        try:
            with requests.get(URL.format(y=y, m=m), stream=True, timeout=60) as r:
                r.raise_for_status()
                with open(tmp, "wb") as f:
                    for chunk in r.iter_content(1 << 20):
                        f.write(chunk)
            tmp.replace(target)
            print(f"{target.name}: {target.stat().st_size / 1e6:.0f} MB")
            return
        except requests.RequestException as e:  # the server drops long transfers now and then
            print(f"{target.name}: attempt {attempt} failed ({e})")
            time.sleep(5 * attempt)
    sys.exit(f"could not download {month}")


if __name__ == "__main__":
    RAW.mkdir(parents=True, exist_ok=True)
    for month in sys.argv[1:] or ["2026-07", "2026-08", "2026-09"]:
        download(month)
