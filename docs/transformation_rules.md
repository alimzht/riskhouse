# Transformation rules

Source-to-target rule catalogue for riskhouse. Every rule ID cited in the SQL (`T-V..`, `T-P..`, `T-S..`,
`T-F..`, `T-M..`, `R1`-`R6`) is defined here. Thresholds are quoted with the dbt variable that holds them
(`dbt_project.yml`, section `vars`).

## 1. Purpose and scope

riskhouse screens Czech public contracts published in **Registr smluv** (the contract register,
data.smlouvy.gov.cz) for warning signs that justify a manual review. It checks each supplier against **ARES**
(the Czech business register, live search plus the commercial register for deleted companies). It converts
foreign-currency values with official **ČNB** (Czech National Bank) daily exchange rates. A second module
analyses a real motor insurance portfolio (**freMTPL2**, French motor third-party liability, 678,013 policies
and 26,639 claims, public domain). The procurement period is **July to September 2026**. Data moves through
three layers:

| Layer | Content | Rule |
|---|---|---|
| Landing / bronze | Source data **as published, every value kept as text** (`ingest/*.py`, `models/*/bronze`) | Nothing is cleaned or dropped |
| Silver | Typed and cleaned: one current version per contract, values in CZK excl. VAT, IČO normalised | Cleaning rules T-V, T-P, T-S, T-F, T-M (section 3) |
| Gold | Screening table (`fct_contract_screening`), data-quality mart, motor segment mart | Screening rules R1-R6 (section 4) |

What is landed: one row per published contract record (a contract *version*) and one row per counterparty
of that version (`parse_contracts.py`). ARES answers are stored as raw JSON, including IČOs ARES does not know
(`found: false`) (`lookup_ares.py`). ČNB rates are kept in the Czech format, e.g. `100 HUF = 6,304`
(`download_cnb_rates.py`). Motor policy and claim files are landed as text (`download_motor.py`).

**Volumes (July-September 2026):** 282,657 published records → 275,570 current contracts; 295,449 counterparty
records; 68,230 distinct IČOs looked up in ARES.

## 2. Principles

| Principle | What it means in practice |
|---|---|
| **Fix vs. flag** | An obvious export error is corrected, and the number of corrections is counted in `mart_procurement_data_quality`. Examples: an IČO missing its leading zeros, a signing date in year 0001. Anything that needs a business decision is **kept and flagged, never silently dropped**. Examples: a missing IČO, an unknown company. |
| **Thresholds are business settings** | Every limit (tender limits, 90 % band, 6-month age, 30-day window, review minutes) is a dbt `var` in `dbt_project.yml`. The reviewing team owns these values and they are version-controlled. Changing a value needs no SQL change. |
| **Every rule is unit-tested** | `models/procurement/procurement_unit_tests.yml` has small hand-made inputs and the expected output, at least one case per rule (run: `dbt test --select test_type:unit`). |
| **One definition per rule** | Each rule is written once in SQL. The rule ID in the SQL comment links it to this document. |
| **Neutral wording** | A flag means "flagged for manual review". It is a warning sign, not a finding. |

## 3. Cleaning rules (silver layer)

"Records affected" are measured counts on the July-September 2026 data.

### 3.1 Contracts (T-V), `models/procurement/silver/stg_contracts.sql`

| ID | Rule | Why | Records affected |
|---|---|---|---|
| T-V01 | A contract can be republished many times. Only the version with the **highest version id** is kept. | A corrected contract must not be counted twice. | 6,563 older versions superseded |
| T-V02 | If that latest version is **withdrawn** (`platnyZaznam = 0`), the contract is excluded. | The publisher has withdrawn the contract, so it is no longer valid. | 524 contracts |
| T-V03 | Value in CZK excl. VAT, in this order of preference: (1) the stated value excl. VAT; (2) the value incl. VAT ÷ (1 + `vat_rate` = 0.21), marked `incl_vat_estimated`; (3) the foreign-currency value × ČNB rate (T-V04). The source used is recorded in `value_basis`. If none is given: `not_stated`, value unknown. | Tender limits are defined excl. VAT. One comparable value is needed. | 48,486 value only incl. VAT; 31,427 no value stated (kept, but R5/R6 cannot apply) |
| T-V04 | A foreign-currency value is converted at the ČNB rate of the signing day. If there is no rate that day (weekend, holiday), the last rate published in the previous 10 days is used. The publication date is used if the signing date is unknown. With no rate found, the value stays unknown (`foreign_currency_no_rate`). | Official rate, reproducible. | 3,495 converted; 1 with no rate found (value unknown) |
| T-V05 | **Construction** is recognised from the free-text subject. After accents are removed, the subject contains *stavb, staveb, rekonstrukc, vystavb, zateplen, demolic, sanac* or *stavebni prace*. Construction gets `tender_limit_construction` = 6,000,000 CZK. Everything else gets `tender_limit_supplies_services` = 2,000,000 CZK. | The register has no contract-type field. Construction has a higher legal tender limit. | 11,701 classified construction |
| T-V06 | A signing date before 2000-01-01 or after the publication date is impossible. It is set to **unknown** and marked `dq_implausible_signed_date`. | These are typos (seen: year 0001 and 2926). Left in, they would distort the date-based rules (R1, R2, R6). | 397 contracts |

### 3.2 Counterparties (T-P), `models/procurement/silver/stg_contract_parties.sql`

Only counterparties of current contract versions (after T-V01/T-V02) are kept.

| ID | Rule | Why | Records affected |
|---|---|---|---|
| T-P01 | A counterparty marked `FO` (*fyzická osoba*, natural person) is an individual. | Individuals often have no IČO. They are not expected to have one (R3/R4 skip them). | 3,285 natural persons |
| T-P02 | Spaces are removed from the IČO. An IČO of 1-8 digits is padded with leading zeros to 8 digits (`6947` → `00006947`). Anything else is `malformed`. Empty values are `missing`. | Exports drop leading zeros. Without padding, the ARES match fails. | 832 IČOs on current contracts published without leading zeros |
| T-P03 | **IČO check digit (mod 11):** each of the first 7 digits is multiplied by the weights 8, 7, 6, 5, 4, 3, 2. Check digit = (11 − sum mod 11) mod 10. It must equal the 8th digit. Otherwise the status is `checksum_failed`. | Catches typos without calling ARES. Implemented once in `macros/cross_engine.sql` (`ico_checksum_ok`). | Companies with missing, malformed or failed-check IČO: see R3 |
| T-P04 | A **foreign supplier** is recognised by a country name in its address (Slovakia, Germany, Austria, Poland, Ireland, Netherlands, USA, UK, France, Hungary, Switzerland, Belgium, Luxembourg, Italy, Spain, Denmark, Sweden; in Czech and English, accents removed). | Foreign suppliers legitimately have no Czech IČO. They are not expected to have one (R3/R4 skip them). | 2,669 foreign suppliers (excluding natural persons) |

### 3.3 Business register (T-S), `models/procurement/silver/stg_ares_companies.sql`

| ID | Rule | Why | Records affected |
|---|---|---|---|
| T-S01 | A company is **in liquidation** when its registered name contains *v likvidaci*. | This is how the register marks a company being wound up. Feeds R2. | see R2 |
| T-S02 | A **public body** is a subject that itself publishes contracts (it appears as a buyer in the register), or one whose legal form is 325 (state organisational unit), 331 (*příspěvková organizace*), 801 (municipality) or 804 (region). | Public bodies have no meaningful founding date, so R1 skips them. | n/a |
| T-S03 | The ARES live search returns **live companies only**. Every IČO it does not find is looked up a second time in the commercial register (*veřejný rejstřík*), where deleted companies keep their name, registration date and deletion date. | Ensures that "dissolved" (R2) is not mistaken for "never existed" (R4). | 1 deleted company found via the commercial register |

### 3.4 Exchange rates (T-F), `models/procurement/silver/stg_cnb_rates.sql`

| ID | Rule | Why | Records affected |
|---|---|---|---|
| T-F01 | ČNB quotes are converted to CZK per **1 unit** of currency (`100 HUF = 6,304` → 0.06304). Czech date (`dd.mm.yyyy`) and decimal-comma formats are parsed, and rows without a rate are dropped. | ČNB quotes some currencies per 100 units. A uniform per-unit rate is needed for T-V04. | n/a (reference data) |

### 3.5 Motor portfolio (T-M), `models/motor/silver/*.sql`, `models/motor/gold/*.sql`

| ID | Rule | Why | Records affected |
|---|---|---|---|
| T-M01 | Exposure (years insured in the period) above 1 is capped at 1.0, marked `dq_exposure_capped`. | A policy-year cannot exceed one year. Values above 1 are data errors. | see mart (`dq_exposure_capped`) |
| T-M02 | More than 4 claims on one policy in a year is capped at 4, marked `dq_claims_capped`. The raw count is kept in `claim_nb_raw`. | Implausible for private motor insurance. | see mart (`dq_claims_capped`) |
| T-M03 | Each single claim is capped at `motor_large_claim_eur` = 100,000 EUR for segment pricing. The uncapped cost and the number of large claims are kept (`claim_cost_eur`, `n_large_claims`). | One catastrophic claim should not set a whole segment's price. | see mart (`n_large_claims`) |
| T-M04 | Rating bands, the way a tariff groups customers: driver age (18-20 … 71+), vehicle age (0 … 13+), vehicle power (4-5 … 10+), bonus-malus (50 best … 125+ malus), population density (<50 … 5000+). | Segments must be large enough to price. | all policies |
| T-M05 | A policy with a claim count but no claim amount in the claims file is marked `dq_claims_without_amount` and kept. | The two source files do not always agree. The gap is shown, not hidden. | see mart (`dq_claims_without_amount`) |

## 4. Screening rules R1-R6 (gold layer), `models/procurement/gold/fct_contract_screening.sql`

Rules are evaluated per **contract × counterparty**. R5 and R6 depend on the contract value (T-V03). A contract
with no known value never triggers them. R6 also needs a known signing date (T-V06).

| ID | Warning sign | Exact condition | Why it matters | Not applied to | Rows flagged |
|---|---|---|---|---|---|
| R1 | **Newly founded supplier** | The supplier was founded fewer than `new_company_days` (182, about 6 months) days before the signing date, or after it. | A company set up just before winning a public contract can be a shell or a front. | Public bodies (T-S02). Suppliers without a founding date (not found in ARES), contracts with an unknown signing date. | 870 |
| R2 | **Dissolved or in-liquidation supplier** | The supplier's dissolution or deletion date is on or before the signing date, **or** the supplier is in liquidation (T-S01). | A contract with a company that no longer exists, or is being wound up, may not be performed. | Suppliers not found in ARES. The date check is skipped when the signing date is unknown (the liquidation check still applies). | 61 |
| R3 | **Company without a valid IČO** | The counterparty's IČO is missing, malformed, or fails the check digit (T-P02, T-P03). | Without a valid company ID the supplier cannot be identified or checked. | Natural persons (T-P01) and foreign suppliers (T-P04) | 8,452 |
| R4 | **IČO unknown to the business register** | The IČO is valid (format and check digit), but neither ARES search nor the commercial register knows it (T-S03). | A well-formed ID that no register knows needs explaining. | Natural persons, foreign suppliers. IČOs with no ARES answer landed at all. | 412 |
| R5 | **Value just under the tender limit** | `value_czk` ≥ `near_limit_share` (0.9) × `tender_limit_czk` **and** `value_czk` < `tender_limit_czk`. At or above the limit a tender is required, so the contract is not flagged. No value means no flag. Limits: `tender_limit_supplies_services` = 2,000,000 CZK, `tender_limit_construction` = 6,000,000 CZK, both excl. VAT (zákon 134/2016 Sb., the Czech public procurement act). | A price just below the limit avoids a public tender. One such contract is normal; many of them are a pattern worth a look. | Contracts with no known value | 1,335 |
| R6 | **Possible contract splitting** | Same buyer **and** same supplier. Only "pieces" count: contracts worth at least `split_min_share` (0.2) × limit and below the limit. Within `split_window_days` (30) days either side of a piece's signing date, the pair has between `split_min_contracts` (2) and `split_max_contracts` (4) pieces, the piece itself included. Together these pieces exceed the tender limit. A contract that lists the same supplier twice counts once. | One purchase split into several contracts below the limit avoids a tender. | Contracts below 20 % of the limit (routine orders). Pairs with more than 4 pieces in the window (recurring call-off ordering). Contracts with no value, no signing date, or no supplier IČO. | 3,298 (was 65,624 before the redesign) |

**Why R6 was redesigned.** The first version had no minimum piece size and no maximum piece count. It flagged
65,624 rows, mostly hospitals' daily drug orders from wholesalers. These are routine call-off orders under
framework agreements, not splitting. The size floor (`split_min_share`) and the piece cap (`split_max_contracts`)
target the pattern that matters: a few sizeable contracts that together cross the limit.

## 5. Review decision

| Outcome | Condition | Meaning |
|---|---|---|
| `review`: **flagged for manual review** | The contract × counterparty row has at least one of R1-R6 (`n_flags` ≥ 1) | A reviewer opens the contract and decides |
| `auto_clear` | No flag | No manual check needed under the current rules |

A flag is a reason to look closer, not proof of wrongdoing. `n_flags` counts how many rules a row triggers. More
flags can be reviewed first.

## 6. Time and cost savings (method)

**Assumption (stated, not measured):** a reviewer spends `review_minutes_low` (5) to `review_minutes_high` (15)
minutes checking one contract by hand. A contract counts as auto-cleared when none of its counterparty rows is
flagged.

Hours saved = auto-cleared contracts × minutes per contract ÷ 60, shown as a range (low, high).

| Item | Formula | Value |
|---|---|---|
| Current contracts screened | count of distinct `contract_id` | **275,570** |
| Contracts flagged for manual review | contracts with ≥ 1 row in `review` | **13,162 (4.8 %)** |
| Auto-cleared contracts | screened − flagged | **262,408** |
| Hours saved, low | auto-cleared × 5 ÷ 60 | **≈ 21,900 h** |
| Hours saved, high | auto-cleared × 15 ÷ 60 | **≈ 65,600 h** |

## 7. Known limitations

| Limitation | Effect | Mitigation |
|---|---|---|
| Construction is classified from keywords in the subject (T-V05) | Some construction contracts get the 2 M limit, and the reverse, which affects R5/R6 | Keyword list is visible and editable. Spot-check during manual review. |
| Foreign suppliers are recognised from a list of country keywords in the address (T-P04) | A foreign supplier from a country not on the list can trigger R3. A Czech address mentioning a listed word can be skipped. | Extend the list as cases appear |
| Natural persons are not always marked `FO` in the register (T-P01) | Individuals without an IČO can trigger R3 | **R3 precision to be measured** by manual review of a 30-contract sample (`docs/checkpoints.md`, checkpoint 2) |
| ARES live search returns live companies only | Without a second lookup, deleted companies would look unknown (false R4) | Second pass in the commercial register (T-S03) |
| No value stated or no exchange rate found (T-V03/T-V04) | R5 and R6 cannot apply to these contracts | Counted in the data-quality mart |
| Hours-saved estimate (section 6) | Rests on the 5-15 minute assumption | Shown as a range. Replace with timed reviews when available. |
