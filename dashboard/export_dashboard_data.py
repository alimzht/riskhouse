"""Export the small, aggregated data the dashboard shows: dashboard/data/dashboard_data.js

    python dashboard/export_dashboard_data.py          (after `python pipeline.py build`)

Only aggregates and a short list of example contracts are exported, so the file is safe to commit and the
dashboard opens from disk or GitHub Pages without running the pipeline. Private individuals (natural persons)
are never listed by name. A flag means "flagged for manual review", not a finding of wrongdoing.
"""
import json
from pathlib import Path

import duckdb

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "dashboard" / "data" / "dashboard_data.js"
EXAMPLES_PER_RULE = 4

RULES = [
    ("r1_new_company", "R1", "Supplier founded < 6 months before signing"),
    ("r2_dissolved", "R2", "Supplier dissolved or in liquidation"),
    ("r3_invalid_ico", "R3", "Company without a valid IČO"),
    ("r4_not_in_register", "R4", "IČO unknown to the business register"),
    ("r5_near_limit", "R5", "Value just under the tender limit"),
    ("r6_split", "R6", "Possible contract splitting"),
]


def rows(con, sql: str) -> list:
    result = con.sql(sql)
    return [dict(zip(result.columns, values)) for values in result.fetchall()]


def main():
    con = duckdb.connect(str(ROOT / "riskhouse.duckdb"), read_only=True)
    screening = "gold.fct_contract_screening"

    summary = rows(con, f"""
        select count(distinct contract_id)                                                   as contracts,
               count(distinct contract_id) filter (where review_queue = 'review')            as flagged,
               min(signed_date)                                                              as first_signed,
               max(signed_date)                                                              as last_signed
        from {screening}""")[0]
    summary["auto_cleared"] = summary["contracts"] - summary["flagged"]
    summary["hours_low"] = round(summary["auto_cleared"] * 5 / 60)
    summary["hours_high"] = round(summary["auto_cleared"] * 15 / 60)
    summary["period"] = "July–September 2026 (publication month)"

    rule_hits = [
        {"rule": code, "label": label,
         "contracts": rows(con, f"select count(distinct contract_id) n from {screening} where {column}")[0]["n"]}
        for column, code, label in RULES
    ]

    # contracts by value around the 2 M CZK limit (supplies & services, value stated excl. VAT)
    histogram = rows(con, """
        select cast(floor(value_czk / 50000) * 50000 as bigint) as bin_start, count(*) as contracts
        from silver.stg_contracts
        where contract_type = 'supplies_services' and value_basis = 'excl_vat'
          and value_czk >= 1000000 and value_czk < 3000000
        group by 1 order by 1""")

    data_quality = rows(con, "select entity, check_name, records, action_taken from gold.mart_procurement_data_quality")

    motor = rows(con, """
        select factor, segment, policies, exposure_years, claims, frequency, severity_eur, pure_premium_eur, relativity
        from gold.mart_motor_segments order by factor, segment""")

    flag_list = " || ".join(f"case when {c} then '{code} ' else '' end" for c, code, _ in RULES)
    examples = []
    for column, code, _ in RULES:
        examples += rows(con, f"""
            select contract_id, url, cast(signed_date as varchar) as signed_date, buyer_name,
                   coalesce(registered_name, party_name) as supplier, value_czk,
                   trim({flag_list}) as flags, '{code}' as example_for
            from {screening}
            where {column} and not is_natural_person and value_czk is not null
            order by value_czk desc
            limit {EXAMPLES_PER_RULE}""")

    payload = {"summary": summary, "rule_hits": rule_hits, "histogram": histogram,
               "data_quality": data_quality, "motor": motor, "examples": examples}
    OUT.parent.mkdir(parents=True, exist_ok=True)
    # a script include, so index.html works from file:// and static hosting (no fetch, no CORS)
    OUT.write_text("window.RISKHOUSE = " + json.dumps(payload, ensure_ascii=False, indent=1, default=str) + ";\n",
                   encoding="utf-8")
    print(f"{OUT.relative_to(ROOT)}: {OUT.stat().st_size / 1024:.0f} KB")


if __name__ == "__main__":
    main()
