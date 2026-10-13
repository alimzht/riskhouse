"""One entry point for the whole pipeline, the same on Windows, macOS and Linux.

    python pipeline.py all          download -> land -> build -> dashboard (first run: ~30 min, mostly ARES lookups)
    python pipeline.py download     raw files: contract dumps, ČNB rates, motor portfolio
    python pipeline.py land         raw -> data/landing: parse contracts, look suppliers up in ARES
    python pipeline.py build        dbt build: bronze -> silver -> gold, with data and unit tests
    python pipeline.py dashboard    export the dashboard data (dashboard/index.html opens without a server)
    python pipeline.py test         pytest (landing code) + dbt unit tests (rules); needs one `build` first,
                                    because dbt unit tests read the column types of the upstream tables

Months and years are settings below; every step skips work that is already done.
"""
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MONTHS = ["2026-07", "2026-08", "2026-09"]   # contract register dumps to screen
FX_YEARS = ["2024", "2025", "2026"]          # ČNB rates: contracts can be signed before they are published


def run(*args: str):
    print(f"\n$ {' '.join(args)}", flush=True)
    env = {**os.environ, "PYTHONIOENCODING": "utf-8"}   # Czech characters on a Windows console
    subprocess.run(args, cwd=ROOT, env=env, check=True)


def python(script: str, *args: str):
    run(sys.executable, script, *args)


def dbt(*args: str):
    run(sys.executable, "-m", "dbt.cli.main", *args, "--profiles-dir", ".")


def download():
    python("ingest/download_contracts.py", *MONTHS)
    python("ingest/download_cnb_rates.py", *FX_YEARS)
    python("ingest/download_motor.py")


def land():
    python("ingest/parse_contracts.py")
    python("ingest/lookup_ares.py")


def build():
    dbt("build")


def dashboard():
    python("dashboard/export_dashboard_data.py")


def test():
    run(sys.executable, "-m", "pytest", "-q", "tests")
    dbt("test", "--select", "test_type:unit")


STEPS = {"download": [download], "land": [land], "build": [build], "dashboard": [dashboard], "test": [test],
         "all": [download, land, build, dashboard]}

if __name__ == "__main__":
    if len(sys.argv) != 2 or sys.argv[1] not in STEPS:
        sys.exit(__doc__)
    for step in STEPS[sys.argv[1]]:
        step()
