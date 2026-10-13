# Checkpoints

Parts of riskhouse written or checked by hand, so every design decision can be explained in person.

## 1. Rule R5: value just under the tender limit (SQL)

**Why it matters.** Under the Czech public procurement act a contract above the limit (2 M CZK excl. VAT for
supplies and services, 6 M CZK for construction) needs a public tender. A contract priced just under the limit
avoids that. One such contract is normal; many of them are a pattern worth a look.

**Where.** `models/procurement/gold/fct_contract_screening.sql`, the line marked `CHECKPOINT 1`, currently
`false as r5_near_limit`.

**What you have in that CTE (`base` columns, all already cleaned):**

| column | meaning |
|---|---|
| `value_czk` | contract value in CZK excl. VAT; NULL when the contract states no value |
| `tender_limit_czk` | 2 000 000 or 6 000 000 depending on `contract_type` |
| `{{ var('near_limit_share') }}` | 0.9, i.e. "within 90-100 % of the limit"; a business setting in `dbt_project.yml` |

**Write** a boolean expression that is true when the value is at least 90 % of the limit and still below it.
Think about: should a contract exactly at the limit count? What happens when `value_czk` is NULL, and what should?

**Check it:**
```bash
dbt build --profiles-dir . --select fct_contract_screening+
```
then count the hits:
```bash
.venv\Scripts\python -c "import duckdb; print(duckdb.connect('riskhouse.duckdb', read_only=True).sql('select contract_type, count(*) from gold.fct_contract_screening where r5_near_limit group by 1'))"
```

**Be ready to say:** why 90 %, why excl. VAT, and why the threshold is a `var` and not a number in the SQL.

## 2. Manual review of 30 flagged contracts

After the rules run on the full data. A random sample of flagged contracts, each opened on smlouvy.gov.cz and
marked "real concern / explainable / data error". Gives the precision of the rules on real data.

## 3. Explain the supplier matching

How a contract's counterparty is matched to the business register (IČO normalisation, check digit, ARES lookup),
and why individuals and foreign suppliers are excluded from the IČO rules.

## 4. One DAX measure in Power BI

With the Power BI report, after applying.
