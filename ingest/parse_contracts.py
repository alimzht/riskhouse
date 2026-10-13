"""Flatten Registr smluv (contract register) XML dumps into two landing tables, every value kept as text.

    python ingest/parse_contracts.py [dump_folder] [output_folder]

Defaults: data/raw/contracts -> data/landing. Writes
    contracts.parquet          one row per published record (a contract *version*)
    contract_parties.parquet   one row per counterparty (smluvniStrana) of that version

Nothing is cleaned here: versions, VAT, currencies and missing IDs are handled in dbt, where every rule
is documented and tested. Dumps are streamed, so memory stays flat whatever the month size.
"""
import sys
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq
from lxml import etree

from paths import LANDING, RAW_CONTRACTS

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
# leaf under <smluvniStrana> -> column name
PARTY_FIELDS = {
    "ico": "party_ico",
    "nazev": "party_name",
    "adresa": "party_address",
    "identifikace": "party_kind",      # 'FO' = natural person (fyzická osoba)
    "prijemce": "party_is_recipient",
    "datovaSchranka": "party_data_box",
}
CONTRACT_COLUMNS = [*CONTRACT_FIELDS.values(), "source_file"]
PARTY_COLUMNS = ["version_id", "party_seq", *PARTY_FIELDS.values(), "source_file"]


def local_name(element) -> str:
    """Tag without its XML namespace: '{http://...}zaznam' -> 'zaznam'."""
    return etree.QName(element).localname


def children(element, name: str):
    return [child for child in element if local_name(child) == name]


def text_at(element, path: str):
    """Stripped text of the first element at a 'a/b/c' path, or None when missing or empty."""
    for part in path.split("/"):
        matches = children(element, part)
        if not matches:
            return None
        element = matches[0]
    return (element.text or "").strip() or None


def iter_records(dump: Path):
    """Yield each <zaznam> element, freeing it afterwards so a 130 MB dump never sits in memory."""
    for _, record in etree.iterparse(str(dump), events=("end",), tag="{*}zaznam",
                                     resolve_entities=False, no_network=True):  # downloaded file: no XXE
        yield record
        record.clear()
        while record.getprevious() is not None:
            del record.getparent()[0]


def to_rows(record, source_file: str):
    """One contract row and its party rows for a single <zaznam>."""
    contract = {column: text_at(record, path) for path, column in CONTRACT_FIELDS.items()}
    contract["source_file"] = source_file

    contract_body = children(record, "smlouva")
    party_elements = children(contract_body[0], "smluvniStrana") if contract_body else []
    parties = [
        {column: text_at(party, field) for field, column in PARTY_FIELDS.items()}
        | {"version_id": contract["version_id"], "party_seq": str(seq), "source_file": source_file}
        for seq, party in enumerate(party_elements, start=1)
    ]
    return contract, parties


def write_table(rows: list, columns: list, target: Path):
    table = pa.table({column: pa.array([row.get(column) for row in rows], pa.string()) for column in columns})
    pq.write_table(table, target)
    print(f"{target.name}: {table.num_rows:,} rows")


def main():
    dump_folder = Path(sys.argv[1]) if len(sys.argv) > 1 else RAW_CONTRACTS   # another folder: CI sample
    output_folder = Path(sys.argv[2]) if len(sys.argv) > 2 else LANDING

    dumps = sorted(dump_folder.glob("dump_*.xml"))
    if not dumps:
        sys.exit(f"no dumps in {dump_folder}; run ingest/download_contracts.py first")
    output_folder.mkdir(parents=True, exist_ok=True)

    contracts, parties = [], []
    for dump in dumps:
        records_before = len(contracts)
        for record in iter_records(dump):
            contract, contract_parties = to_rows(record, dump.name)
            contracts.append(contract)
            parties.extend(contract_parties)
        print(f"{dump.name}: {len(contracts) - records_before:,} records")

    write_table(contracts, CONTRACT_COLUMNS, output_folder / "contracts.parquet")
    write_table(parties, PARTY_COLUMNS, output_folder / "contract_parties.parquet")


if __name__ == "__main__":
    main()
