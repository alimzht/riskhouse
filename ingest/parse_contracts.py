"""Flatten Registr smluv (contract register) XML dumps into two landing tables, every value kept as text.

    python ingest/parse_contracts.py            # all data/raw/contracts/dump_*.xml

data/landing/contracts.parquet          one row per published record (a contract *version*)
data/landing/contract_parties.parquet   one row per counterparty (smluvniStrana) of that version

Nothing is cleaned here: versions, VAT, currencies and missing IDs are handled in dbt, where every rule
is documented and tested. Dumps are streamed, so memory stays flat whatever the month size.
"""
import sys
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq
from lxml import etree

from paths import LANDING, RAW_CONTRACTS

RAW = RAW_CONTRACTS
OUT = LANDING

# leaf path under <zaznam> -> column name
CONTRACT_FIELDS = {
    "identifikator/idSmlouvy": "contract_id",
    "identifikator/idVerze": "version_id",
    "odkaz": "url",
    "casZverejneni": "published_at",
    "platnyZaznam": "is_valid_record",
    "smlouva/predmet": "subject",
    "smlouva/datumUzavreni": "signed_date",
    "smlouva/cisloSmlouvy": "contract_number",
    "smlouva/hodnotaBezDph": "value_excl_vat",
    "smlouva/hodnotaVcetneDph": "value_incl_vat",
    "smlouva/ciziMena/hodnota": "foreign_value",
    "smlouva/ciziMena/mena": "foreign_currency",
    "smlouva/cenaNeuvedena": "price_not_stated_reason",
    "smlouva/navazanyZaznam": "linked_version_id",
    "smlouva/subjekt/ico": "buyer_ico",
    "smlouva/subjekt/nazev": "buyer_name",
    "smlouva/subjekt/adresa": "buyer_address",
    "smlouva/subjekt/platce": "buyer_is_payer",
}
PARTY_FIELDS = {
    "ico": "party_ico",
    "nazev": "party_name",
    "adresa": "party_address",
    "identifikace": "party_kind",      # 'FO' = natural person (fyzická osoba)
    "prijemce": "party_is_recipient",
    "datovaSchranka": "party_data_box",
}


def local(el) -> str:
    return etree.QName(el).localname


def text_at(record, path: str):
    node = record
    for part in path.split("/"):
        node = next((c for c in node if local(c) == part), None)
        if node is None:
            return None
    value = (node.text or "").strip()
    return value or None


def parse(path: Path, contracts: list, parties: list):
    for _, rec in etree.iterparse(str(path), events=("end",), tag="{*}zaznam"):
        row = {col: text_at(rec, p) for p, col in CONTRACT_FIELDS.items()}
        row["source_file"] = path.name
        contracts.append(row)
        smlouva = next((c for c in rec if local(c) == "smlouva"), None)
        for i, party in enumerate(c for c in (smlouva if smlouva is not None else []) if local(c) == "smluvniStrana"):
            p = {col: text_at(party, f) for f, col in PARTY_FIELDS.items()}
            p.update(version_id=row["version_id"], party_seq=str(i + 1), source_file=path.name)
            parties.append(p)
        rec.clear()  # free the parsed record and its finished siblings
        while rec.getprevious() is not None:
            del rec.getparent()[0]


def write(rows: list, columns: list, name: str):
    table = pa.table({c: pa.array([r.get(c) for r in rows], pa.string()) for c in columns})
    pq.write_table(table, OUT / name)
    print(f"{name}: {table.num_rows:,} rows")


def main():
    global OUT
    raw = Path(sys.argv[1]) if len(sys.argv) > 1 else RAW   # optional: another dump folder (CI sample)
    OUT = Path(sys.argv[2]) if len(sys.argv) > 2 else OUT
    files = sorted(raw.glob("dump_*.xml"))
    if not files:
        sys.exit(f"no dumps in {raw}; run ingest/download_contracts.py first")
    OUT.mkdir(parents=True, exist_ok=True)
    contracts, parties = [], []
    for f in files:
        before = len(contracts)
        parse(f, contracts, parties)
        print(f"{f.name}: {len(contracts) - before:,} records")
    write(contracts, list(CONTRACT_FIELDS.values()) + ["source_file"], "contracts.parquet")
    write(parties, ["version_id", "party_seq"] + list(PARTY_FIELDS.values()) + ["source_file"], "contract_parties.parquet")


if __name__ == "__main__":
    main()
