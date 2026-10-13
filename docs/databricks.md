# Running riskhouse on Databricks (Free Edition)

Development runs on DuckDB. Production runs the same dbt project on Databricks: only bronze differs
(`macros/landing.sql`), it reads Delta tables `workspace.landing.<name>` instead of the local landing files.

**Security:** the access token is a password. Never paste it into chat, a notebook, a screenshot or any
committed file. It lives only in environment variables of your own shell (or a gitignored `.env`).

## 1. Produce the landing files locally

```powershell
python pipeline.py download
python pipeline.py land
```

This fills `data/landing/` with `contracts.parquet`, `contract_parties.parquet`, `cnb_rates.parquet`,
`motor_policies.parquet`, `motor_claims.parquet`, `ares_raw.jsonl`, `ares_deleted.jsonl`.

## 2. Create the landing schema and volume

In the Databricks workspace open **SQL Editor** and run:

```sql
create schema if not exists workspace.landing;
create volume if not exists workspace.landing.files;
```

## 3. Upload the landing files

**Catalog** -> `workspace` -> `landing` -> Volumes -> `files` -> **Upload to this volume**, and select every
file in `data/landing/`. They end up in `/Volumes/workspace/landing/files/`.

## 4. Load them into Delta tables

**Workspace** -> your folder -> **Import** -> File -> `notebooks/01_land.py`. Open it, attach **Serverless**
compute and **Run all**. Widgets: `catalog` = `workspace`, `raw_path` = `/Volumes/workspace/landing/files`.

The notebook creates `workspace.landing.<name>` for every table in `models/sources.yml` and ends with a
reconciliation cell that asserts each Delta table has exactly as many rows as its source file.

## 5. Connection details as environment variables

Find the values (see `.env.example`):

- **Server hostname** and **HTTP path**: SQL Warehouses -> your warehouse -> Connection details.
- **Token**: Settings -> Developer -> Access tokens -> Generate new token.

Set them in the PowerShell session you run dbt from (they vanish when the window closes; nothing is written
to disk or committed):

```powershell
$env:DATABRICKS_HOST = "dbc-xxxxxxxx-xxxx.cloud.databricks.com"
$env:DATABRICKS_HTTP_PATH = "/sql/1.0/warehouses/xxxxxxxxxxxxxxxx"
$env:DATABRICKS_TOKEN = Read-Host "Databricks token"     # typed, not stored in shell history
$env:DATABRICKS_CATALOG = "workspace"
```

`.env` is gitignored if you prefer a file; `.env.example` is the committed template with placeholders only.

## 6. Build

```powershell
pip install dbt-databricks
dbt build --target databricks --profiles-dir .
```

This creates the schemas `bronze`, `silver` and `gold` in the catalog, runs the data tests and the unit tests.

## 7. Check the result

In the SQL Editor:

```sql
select review_queue, count(*) as contracts
from workspace.gold.fct_contract_screening
group by review_queue
order by review_queue;
```

`review` rows are contracts flagged for manual review; `auto_clear` rows raised no rule. The counts should
match the same query on the local DuckDB build of the same landing files.
