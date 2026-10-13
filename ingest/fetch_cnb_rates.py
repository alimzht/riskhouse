"""Download official ČNB (Czech National Bank) daily exchange rates and land them as text.

    python ingest/fetch_cnb_rates.py 2026            # one or more years

data/landing/cnb_rates.parquet: rate_date '02.01.2026', unit '100', currency 'HUF', rate '6,304'.
Kept exactly as published (Czech date and decimal formats, per-unit quotes); dbt converts them.
"""
import sys
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq
import requests

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "landing" / "cnb_rates.parquet"
URL = "https://www.cnb.cz/cs/financni-trhy/devizovy-trh/kurzy-devizoveho-trhu/kurzy-devizoveho-trhu/rok.txt?rok={year}"


def rows_for(year: str):
    text = requests.get(URL.format(year=year), timeout=60).text
    header = None
    for line in text.splitlines():
        cells = line.strip().split("|")
        if cells[0] == "Datum":            # header row, repeated when the currency list changes
            header = [c.split(" ") for c in cells[1:]]   # '100 HUF' -> ['100', 'HUF']
            continue
        if header and len(cells) == len(header) + 1:
            for (unit, currency), rate in zip(header, cells[1:]):
                yield {"rate_date": cells[0], "unit": unit, "currency": currency, "rate": rate}


if __name__ == "__main__":
    years = sys.argv[1:] or ["2026"]
    rows = [r for y in years for r in rows_for(y)]
    OUT.parent.mkdir(parents=True, exist_ok=True)
    pq.write_table(pa.table({k: pa.array([r[k] for r in rows], pa.string())
                             for k in ["rate_date", "unit", "currency", "rate"]}), OUT)
    print(f"{OUT.name}: {len(rows):,} rows for {', '.join(years)}")
