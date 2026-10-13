"""Download freMTPL2 (real French motor third-party liability portfolio, CC0) from OpenML and land it as text.

    python ingest/download_motor.py

data/landing/motor_policies.parquet  678,013 policies: exposure, claim count, driver/vehicle/region factors
data/landing/motor_claims.parquet    26,639 claims: policy id and claim amount (EUR)
The portfolio has no premiums, so the motor module estimates expected claim cost, not loss ratios.
"""
import csv
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq
import requests

from paths import LANDING, RAW_MOTOR

FILES = {  # OpenML file id -> (name, landing table)
    "20649148": ("freMTPL2freq", "motor_policies"),
    "20649149": ("freMTPL2sev", "motor_claims"),
}


def arff_to_table(path: Path) -> pa.Table:
    columns, rows, in_data = [], [], False
    with open(path, encoding="utf-8") as f:
        for line in f:
            s = line.strip()
            if not s or s.startswith("%"):
                continue
            if not in_data:
                low = s.lower()
                if low.startswith("@attribute"):
                    columns.append(s.split()[1].strip("'\""))
                elif low.startswith("@data"):
                    in_data = True
                continue
            rows.append(next(csv.reader([s], quotechar="'", skipinitialspace=True)))
    return pa.table({c: pa.array([r[i] for r in rows], pa.string()) for i, c in enumerate(columns)})


if __name__ == "__main__":
    RAW_MOTOR.mkdir(parents=True, exist_ok=True)
    LANDING.mkdir(parents=True, exist_ok=True)
    for file_id, (name, table) in FILES.items():
        target = RAW_MOTOR / f"{name}.arff"
        if not target.exists():
            r = requests.get(f"https://openml.org/data/v1/download/{file_id}/{name}.arff", timeout=300)
            r.raise_for_status()
            target.write_bytes(r.content)
        t = arff_to_table(target)
        pq.write_table(t, LANDING / f"{table}.parquet")
        print(f"{table}.parquet: {t.num_rows:,} rows, columns {t.column_names}")
