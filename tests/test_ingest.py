"""Tests for the landing scripts: run with `pytest`."""
import sys
from pathlib import Path

import pyarrow.parquet as pq

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "ingest"))

import lookup_ares  # noqa: E402
import parse_contracts  # noqa: E402

FIXTURES = ROOT / "tests" / "fixtures" / "contracts"


def test_ico_normalisation():
    assert lookup_ares.normalise_ico("27082440") == "27082440"
    assert lookup_ares.normalise_ico("6947") == "00006947"       # published without leading zeros
    assert lookup_ares.normalise_ico(" 2708 2440 ") == "27082440"
    assert lookup_ares.normalise_ico("CZ27082440") is None       # VAT number, not an IČO
    assert lookup_ares.normalise_ico("123456789") is None        # too long
    assert lookup_ares.normalise_ico(None) is None


def test_parse_contracts(tmp_path, monkeypatch):
    monkeypatch.setattr(sys, "argv", ["parse_contracts.py", str(FIXTURES), str(tmp_path)])
    parse_contracts.main()

    contracts = pq.read_table(tmp_path / "contracts.parquet").to_pylist()
    parties = pq.read_table(tmp_path / "contract_parties.parquet").to_pylist()

    assert [c["contract_id"] for c in contracts] == ["100", "200"]
    first = contracts[0]
    assert first["value_excl_vat"] == "1950000"          # kept as text, not parsed
    assert first["buyer_ico"] == "00000001"
    assert first["subject"] == "Rekonstrukce chodníku"     # Czech characters survive
    assert contracts[1]["foreign_value"] == "1000" and contracts[1]["foreign_currency"] == "EUR"

    assert len(parties) == 3                                # two parties on contract 100, one on 200
    assert parties[1]["party_kind"] == "FO" and parties[1]["party_ico"] is None
    assert {p["version_id"] for p in parties} == {"1001", "2001"}
