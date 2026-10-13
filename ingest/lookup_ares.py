"""Look up every contract counterparty in ARES (the Czech business register) and land the answers.

    python ingest/lookup_ares.py

Reads the IČO (company ID) of every party in data/landing/contract_parties.parquet, asks the ARES REST API
in batches, and keeps each answer as raw JSON in data/landing/ares_raw.jsonl. An IČO ARES does not know is
recorded too ('found': false), because "not in the register" is itself a finding (rule R4).
Re-running only asks for IČOs not landed before, so a dropped connection costs nothing.

IČOs are padded to 8 digits for the request ('6947' -> '00006947'); dbt applies the same normalisation
when it joins (models/procurement/silver/stg_contract_parties.sql).
"""
import json
import re
import sys
import time

import pyarrow.parquet as pq
import requests

from paths import LANDING

PARTIES = LANDING / "contract_parties.parquet"
OUT = LANDING / "ares_raw.jsonl"
DELETED_OUT = LANDING / "ares_deleted.jsonl"
URL = "https://ares.gov.cz/ekonomicke-subjekty-v-be/rest/ekonomicke-subjekty/vyhledat"
# The search above returns live subjects only. A company deleted from the commercial register (veřejný rejstřík)
# is still served here, with its deletion date, so "dissolved" (R2) is not mistaken for "never existed" (R4).
DELETED_URL = "https://ares.gov.cz/ekonomicke-subjekty-v-be/rest/ekonomicke-subjekty-vr/{ico}"

BATCH_SIZE = 100               # the most IČOs ARES accepts in one search
PAUSE_SECONDS = 0.3            # between batches: be polite to a public service
RETRY_ATTEMPTS = 5             # back-off grows 5 s, 10 s, 15 s ...
PROGRESS_EVERY_BATCHES = 20    # one progress line per 2 000 IČOs


def normalise_ico(ico):
    """8-digit IČO, or None when the value cannot be one ('CZ27082440', too long, empty)."""
    digits = re.sub(r"\s", "", ico or "")
    return digits.zfill(8) if digits.isdigit() and len(digits) <= 8 else None


def wanted_icos() -> set:
    published = pq.read_table(PARTIES, columns=["party_ico"]).column(0).to_pylist()
    return {normalise_ico(ico) for ico in published} - {None}


def read_landed(path) -> list:
    """Lines landed so far. A last line cut off by an interrupted run is skipped and asked again."""
    if not path.exists():
        return []
    landed = []
    for line in path.read_text(encoding="utf-8").splitlines():
        try:
            landed.append(json.loads(line))
        except json.JSONDecodeError:
            pass
    return landed


def landed_icos() -> set:
    return {line["ico"] for line in read_landed(OUT)}


def lookup_batch(icos: list) -> dict:
    """ARES answers for a batch, keyed by IČO. IČOs ARES does not know are simply absent."""
    for attempt in range(1, RETRY_ATTEMPTS + 1):
        try:
            response = requests.post(URL, json={"ico": icos, "pocet": BATCH_SIZE, "start": 0}, timeout=60)
            if response.status_code == 404:          # none of the batch exists
                return {}
            response.raise_for_status()
            return {subject["ico"]: subject for subject in response.json().get("ekonomickeSubjekty", [])}
        except requests.RequestException as error:
            print(f"  attempt {attempt} failed ({error})")
            time.sleep(5 * attempt)
    raise SystemExit("ARES not reachable")


def main():
    sys.stdout.reconfigure(encoding="utf-8")  # Czech characters on a Windows console
    wanted, landed = wanted_icos(), landed_icos()
    todo = sorted(wanted - landed)
    print(f"{len(wanted):,} distinct IČOs, {len(landed):,} already landed, {len(todo):,} to ask")

    with open(OUT, "a", encoding="utf-8") as out:
        for batch_no, start in enumerate(range(0, len(todo), BATCH_SIZE)):
            batch = todo[start:start + BATCH_SIZE]
            answers = lookup_batch(batch)
            fetched_at = time.strftime("%Y-%m-%dT%H:%M:%S")
            for ico in batch:
                line = {"ico": ico, "found": ico in answers, "fetched_at": fetched_at, "subject": answers.get(ico)}
                out.write(json.dumps(line, ensure_ascii=False) + "\n")
            if batch_no % PROGRESS_EVERY_BATCHES == 0:
                print(f"  {start + len(batch):,}/{len(todo):,}")
            time.sleep(PAUSE_SECONDS)
    lookup_deleted()
    print("done")


def lookup_deleted():
    """Second pass: ask the commercial register about every IČO the live search did not know."""
    not_found = {line["ico"] for line in read_landed(OUT) if not line["found"]}
    todo = sorted(not_found - {line["ico"] for line in read_landed(DELETED_OUT)})
    print(f"{len(not_found):,} IČOs not in the live register, {len(todo):,} to check for a deleted company")
    with open(DELETED_OUT, "a", encoding="utf-8") as out:
        for ico in todo:
            for attempt in range(1, RETRY_ATTEMPTS + 1):
                try:
                    response = requests.get(DELETED_URL.format(ico=ico), timeout=60)
                    if response.status_code not in (200, 404):
                        response.raise_for_status()
                    break
                except requests.RequestException as error:
                    print(f"  {ico}: attempt {attempt} failed ({error})")
                    time.sleep(5 * attempt)
            else:
                raise SystemExit("ARES not reachable")
            record = response.json() if response.status_code == 200 else None
            line = {"ico": ico, "found": record is not None,
                    "fetched_at": time.strftime("%Y-%m-%dT%H:%M:%S"), "record": record}
            out.write(json.dumps(line, ensure_ascii=False) + "\n")
            time.sleep(PAUSE_SECONDS)


if __name__ == "__main__":
    main()
