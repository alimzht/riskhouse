{# Bronze is the only engine-specific layer.
   DuckDB (local): read the landing file directly.
   Spark / Databricks: notebooks/01_land.py has loaded the same landing file into a Delta table
   (schema 'landing'), so bronze reads that table. Columns are identical on both. #}
{% macro landing(name, reader) -%}
    {{ return(adapter.dispatch('landing')(name, reader)) }}
{%- endmacro %}

{% macro default__landing(name, reader) -%}
    {{ reader }}
{%- endmacro %}

{% macro spark__landing(name, reader) -%}
    {{ source('landing', name) }}
{%- endmacro %}

{% macro landing_parquet(name) -%}
    {{ landing(name, "read_parquet('" ~ var('landing_path') ~ "/" ~ name ~ ".parquet')") }}
{%- endmacro %}
