"""Build the tiny landing sample CI runs on, deterministically, so it is reproducible and reviewable.

    python tests/fixtures/make_landing_sample.py

Writes tests/fixtures/landing/ with exactly the files, columns and types the dbt bronze layer reads from
data/landing/ (real data is downloaded by ingest/ and never committed):

    contracts.parquet, contract_parties.parquet   ingest/parse_contracts.py run on tests/fixtures/contracts
    cnb_rates.parquet                             ČNB rates as published: Czech dates and decimal commas, all text
    ares_raw.jsonl                                one ARES answer per valid IČO among the fixture parties
    ares_deleted.jsonl                            commercial-register answers; empty, every fixture IČO is live
    motor_policies.parquet, motor_claims.parquet  20 policies / 5 claims, freMTPL2 column names, all text

CI then runs: dbt build --target ci --vars '{landing_path: tests/fixtures/landing}'
"""
import json
import subprocess
import sys
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OUT = HERE / "landing"
FETCHED_AT = "2026-01-10T12:00:00"   # fixed, so re-running produces identical files


def write_text_table(name: str, rows: list, columns: list):
    """All-string parquet, like every landing script writes."""
    table = pa.table({c: pa.array([r[c] for r in rows], pa.string()) for c in columns})
    pq.write_table(table, OUT / f"{name}.parquet")
    print(f"{name}.parquet: {table.num_rows} rows")


def contracts():
    """The real parser on the committed XML fixture: the sample is exactly what landing would produce."""
    subprocess.run([sys.executable, str(ROOT / "ingest" / "parse_contracts.py"),
                    str(HERE / "contracts"), str(OUT)], check=True)


def cnb_rates():
    # Late December 2025 and early January 2026: a contract signed 2026-01-03 (a Saturday) takes the
    # rate of Friday 2026-01-02 (T-V04: signing day or the last trading day before it).
    published = [
        ("29.12.2025", "24,320", "21,210", "6,215"),
        ("30.12.2025", "24,295", "21,180", "6,220"),
        ("31.12.2025", "24,270", "21,150", "6,231"),
        ("02.01.2026", "24,255", "21,100", "6,240"),
        ("05.01.2026", "24,240", "21,050", "6,304"),
    ]
    rows = []
    for rate_date, eur, usd, huf in published:
        rows += [
            {"rate_date": rate_date, "unit": "1", "currency": "EUR", "rate": eur},
            {"rate_date": rate_date, "unit": "1", "currency": "USD", "rate": usd},
            {"rate_date": rate_date, "unit": "100", "currency": "HUF", "rate": huf},
        ]
    write_text_table("cnb_rates", rows, ["rate_date", "unit", "currency", "rate"])


# Realistic ARES answers (shape of the /ekonomicke-subjekty/vyhledat response), keyed by IČO.
# Every valid IČO among the fixture parties needs one (tests/ares_answer_for_every_valid_ico.sql).
ARES_SUBJECTS = {
    "27082440": {
        "ico": "27082440",
        "obchodniJmeno": "Dodavatel s.r.o.",
        "sidlo": {
            "kodStatu": "CZ",
            "nazevStatu": "Česká republika",
            "kodKraje": 19,
            "nazevKraje": "Hlavní město Praha",
            "nazevObce": "Praha",
            "nazevUlice": "Jankovcova",
            "cisloDomovni": 1522,
            "psc": 17000,
            "textovaAdresa": "Jankovcova 1522/53, Holešovice, 17000 Praha 7",
        },
        "pravniForma": "112",
        "financniUrad": "007",
        "datumVzniku": "2003-08-26",
        "datumAktualizace": "2025-11-20",
        "dic": "CZ27082440",
        "icoId": "27082440",
        "czNace": ["4791", "47410", "620"],
        "primarniZdroj": "vr",
    },
}


def ares():
    with open(OUT / "ares_raw.jsonl", "w", encoding="utf-8", newline="\n") as out:
        for ico, subject in sorted(ARES_SUBJECTS.items()):
            line = {"ico": ico, "found": True, "fetched_at": FETCHED_AT, "subject": subject}
            out.write(json.dumps(line, ensure_ascii=False) + "\n")
    # Every fixture IČO is found by the live search, so the deleted-company pass had nothing to ask.
    # An empty file is valid for DuckDB read_json (0 rows) and for the Databricks landing notebook.
    (OUT / "ares_deleted.jsonl").write_text("", encoding="utf-8")
    print(f"ares_raw.jsonl: {len(ARES_SUBJECTS)} lines, ares_deleted.jsonl: 0 lines")


def motor():
    areas, brands, gases, regions = "ABCDEF", ["B1", "B2", "B3", "B12"], ["Regular", "Diesel"], \
        ["R11", "R24", "R52", "R82", "R93"]
    claim_counts = {3: 1, 7: 2, 12: 1, 18: 1}             # IDpol -> ClaimNb
    policies = []
    for i in range(1, 21):
        policies.append({
            "IDpol": f"{i}.0",
            "ClaimNb": f"{claim_counts.get(i, 0)}.0",
            "Exposure": ["0.1", "0.5", "0.77", "1.0", "1.2"][i % 5],   # 1.2 exercises the exposure cap (T-M01)
            "Area": areas[i % 6],
            "VehPower": f"{4 + i % 9}.0",
            "VehAge": f"{(i * 3) % 17}.0",
            "DrivAge": f"{19 + (i * 7) % 60}.0",
            "BonusMalus": f"{[50, 50, 68, 85, 100, 125][i % 6]}.0",
            "VehBrand": brands[i % 4],
            "VehGas": gases[i % 2],
            "Density": f"{[27, 120, 760, 3000, 9000][i % 5]}.0",
            "Region": regions[i % 5],
        })
    write_text_table("motor_policies", policies, ["IDpol", "ClaimNb", "Exposure", "Area", "VehPower", "VehAge",
                                                  "DrivAge", "BonusMalus", "VehBrand", "VehGas", "Density",
                                                  "Region"])
    claims = [("3", "1204.0"), ("7", "850.5"), ("7", "2310.0"), ("12", "145000.0"), ("18", "999.0")]
    write_text_table("motor_claims", [{"IDpol": p, "ClaimAmount": a} for p, a in claims],
                     ["IDpol", "ClaimAmount"])


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    OUT.mkdir(parents=True, exist_ok=True)
    contracts()
    cnb_rates()
    ares()
    motor()
