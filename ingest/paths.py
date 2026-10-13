"""Where the landing scripts read and write. One place, so a folder move is a one-line change."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW_CONTRACTS = ROOT / "data" / "raw" / "contracts"   # Registr smluv XML dumps, as downloaded
RAW_MOTOR = ROOT / "data" / "raw" / "motor"           # freMTPL2 ARFF files, as downloaded
LANDING = ROOT / "data" / "landing"                   # parquet / jsonl the dbt bronze layer reads
