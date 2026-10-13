# Databricks notebook source
# MAGIC %md
# MAGIC # 01 Land: landing files -> Delta tables `<catalog>.landing.<name>`
# MAGIC
# MAGIC The Databricks counterpart of reading `data/landing/*` directly on DuckDB. It loads the files produced by
# MAGIC `ingest/` (uploaded to a Unity Catalog volume, see `docs/databricks.md`) into Delta tables with **exactly
# MAGIC the same columns** the DuckDB bronze layer sees, so dbt bronze on Databricks (`source('landing', name)`,
# MAGIC `macros/landing.sql`) and on DuckDB are interchangeable:
# MAGIC
# MAGIC | file | Delta table columns |
# MAGIC |---|---|
# MAGIC | `contracts`, `contract_parties`, `cnb_rates`, `motor_policies`, `motor_claims` (.parquet) | as in the file, every column a string |
# MAGIC | `ares_raw.jsonl` | `ico` string, `found` boolean, `fetched_at` string, `subject` JSON **text** |
# MAGIC | `ares_deleted.jsonl` | `ico` string, `found` boolean, `fetched_at` string, `record` JSON **text** |
# MAGIC
# MAGIC `subject` / `record` must hold the raw JSON text: silver reads them with `get_json_object(subject, '$.path')`
# MAGIC (`macros/cross_engine.sql`, `spark__json_text`). A JSON `null` (IČO not found) lands as SQL NULL, as on DuckDB.
# MAGIC
# MAGIC Runs on serverless compute. Re-running replaces the tables (idempotent).

# COMMAND ----------

dbutils.widgets.text("catalog", "workspace", "Unity Catalog catalog")
dbutils.widgets.text("raw_path", "/Volumes/workspace/landing/files", "Folder with the landing files")

catalog = dbutils.widgets.get("catalog").strip()
raw_path = dbutils.widgets.get("raw_path").strip().rstrip("/")

# Same list as models/sources.yml (source 'landing')
PARQUET_TABLES = ["contracts", "contract_parties", "cnb_rates", "motor_policies", "motor_claims"]
JSONL_TABLES = {"ares_raw": "subject", "ares_deleted": "record"}   # table -> name of its raw-JSON column

spark.sql(f"create schema if not exists `{catalog}`.landing")
print(f"landing {raw_path} -> {catalog}.landing")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Parquet files: as-is
# MAGIC The landing scripts write every column as text, so the Delta table keeps string columns, no casting.
# MAGIC No extra columns (e.g. a source-file column) are added: bronze is `select *`, and the columns must match DuckDB.

# COMMAND ----------

from pyspark.sql import functions as F
from pyspark.sql.types import StringType


def save(df, name):
    (df.write.format("delta").mode("overwrite").option("overwriteSchema", "true")
       .saveAsTable(f"`{catalog}`.landing.{name}"))


for name in PARQUET_TABLES:
    df = spark.read.parquet(f"{raw_path}/{name}.parquet")
    not_text = [f.name for f in df.schema.fields if not isinstance(f.dataType, StringType)]
    assert not not_text, f"{name}.parquet: landing columns must be text, found non-string {not_text}"
    save(df, name)
    print(f"{name}: {len(df.columns)} columns")

# COMMAND ----------

# MAGIC %md
# MAGIC ## ARES JSON lines: three typed fields + the raw JSON object as text
# MAGIC An explicit schema with `subject` as StringType is not reliable for a nested object, so each line is read as
# MAGIC plain text: `from_json` types the three scalar fields, `get_json_object(value, '$.subject')` keeps the nested
# MAGIC object as its JSON text (and returns NULL for a JSON `null`).

# COMMAND ----------

SCALARS = "ico string, found boolean, fetched_at string"


def jsonl_lines(name):
    """Non-blank lines of a JSONL file, one row each (column `value`). An empty file gives 0 rows."""
    return spark.read.text(f"{raw_path}/{name}.jsonl").where(F.trim("value") != "")


for name, json_col in JSONL_TABLES.items():
    parsed = (jsonl_lines(name)
              .select(F.from_json("value", SCALARS).alias("s"),
                      F.get_json_object("value", f"$.{json_col}").alias(json_col))
              .select(F.col("s.ico").cast("string").alias("ico"),
                      F.col("s.found").cast("boolean").alias("found"),
                      F.col("s.fetched_at").cast("string").alias("fetched_at"),
                      F.col(json_col).cast("string").alias(json_col)))
    save(parsed, name)
    print(f"{name}: columns {parsed.columns}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Reconciliation: every source row landed, nothing more
# MAGIC Row count of each Delta table = rows in its source file. For JSONL also: every line parsed (an unparsable
# MAGIC line would give a NULL `ico` / `found`), and a found IČO carries its JSON object.

# COMMAND ----------

results = []
for name in PARQUET_TABLES + list(JSONL_TABLES):
    if name in JSONL_TABLES:
        source_rows = jsonl_lines(name).count()
    else:
        source_rows = spark.read.parquet(f"{raw_path}/{name}.parquet").count()
    table_rows = spark.table(f"`{catalog}`.landing.{name}").count()
    results.append((name, source_rows, table_rows, source_rows == table_rows))

display(spark.createDataFrame(results, "table string, source_rows long, delta_rows long, match boolean"))
mismatched = [r for r in results if not r[3]]
assert not mismatched, f"row counts differ between file and Delta table: {mismatched}"

for name, json_col in JSONL_TABLES.items():
    t = spark.table(f"`{catalog}`.landing.{name}")
    unparsed = t.where("ico is null or found is null").count()
    assert unparsed == 0, f"{name}: {unparsed} lines without a parsable ico/found"
    found_without_json = t.where(f"found and {json_col} is null").count()
    assert found_without_json == 0, f"{name}: {found_without_json} found IČOs without their JSON {json_col}"

print("reconciliation OK: all landing tables match their source files")
