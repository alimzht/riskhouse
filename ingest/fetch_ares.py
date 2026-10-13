"""Look up every contract counterparty in ARES (the Czech business register) and land the answers.

    python ingest/fetch_ares.py

Reads the IČO (company ID) of every party in data/landing/contract_parties.parquet, asks the ARES REST API
100 at a time, and keeps each answer as raw JSON in data/landing/ares_raw.jsonl. An IČO ARES does not
know is recorded too ('found': false), because "not in the register" is itself a finding (rule R4).
Re-running only asks for IČOs not seen before, so a dropped connection costs nothing.

IČOs are padded to 8 digits for the request ('6947' -> '00006947'); dbt applies the same normalisation
when it joins, see models/procurement/silver.
"""
import json
import re
import sys
import time
from pathlib import Path

import pyarrow.parquet as pq
import requests

ROOT = Path(__file__).resolve().parents[1]
PARTIES = ROOT / "data" / "landing" / "contract_parties.parquet"
OUT = ROOT / "data" / "landing" / "ares_raw.jsonl"
URL = "https://ares.gov.cz/ekonomicke-subjekty-v-be/rest/ekonomicke-subjekty/vyhledat"
BATCH = 100


def normalise(ico):
    digits = re.sub(r"\s", "", ico or "")
    return digits.zfill(8) if digits.isdigit() and len(digits) <= 8 else None


def ask(icos, attempts=5):
    for attempt in range(1, attempts + 1):
        try:
            r = requests.post(URL, json={"ico": icos, "pocet": BATCH, "start": 0}, timeout=60)
            if r.status_code == 404:          # none of the batch exists
                return []
            r.raise_for_status()
            return r.json().get("ekonomickeSubjekty", [])
        except requests.RequestException as e:
            print(f"  attempt {attempt} failed ({e})")
            time.sleep(5 * attempt)
    raise SystemExit("ARES not reachable")


def main():
    sys.stdout.reconfigure(encoding="utf-8")  # Czech characters on a Windows console
    wanted = {normalise(i) for i in pq.read_table(PARTIES, columns=["party_ico"]).column(0).to_pylist()} - {None}
    seen = set()
    if OUT.exists():
        seen = {json.loads(line)["ico"] for line in OUT.read_text(encoding="utf-8").splitlines()}
    todo = sorted(wanted - seen)
    print(f"{len(wanted):,} distinct IČOs, {len(seen):,} already landed, {len(todo):,} to ask")
    with open(OUT, "a", encoding="utf-8") as f:
        for i in range(0, len(todo), BATCH):
            batch = todo[i:i + BATCH]
            found = {s["ico"]: s for s in ask(batch)}
            fetched_at = time.strftime("%Y-%m-%dT%H:%M:%S")
            for ico in batch:
                f.write(json.dumps({"ico": ico, "found": ico in found, "fetched_at": fetched_at,
                                    "subject": found.get(ico)}, ensure_ascii=False) + "\n")
            if (i // BATCH) % 20 == 0:
                print(f"  {i + len(batch):,}/{len(todo):,}")
            time.sleep(0.3)  # be polite to a public service
    print("done")


if __name__ == "__main__":
    main()
