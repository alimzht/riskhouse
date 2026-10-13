{# Engine-specific SQL lives only here. default__ = DuckDB (local), spark__ = Spark / Databricks.
   Models call the macro, so silver and gold are the same SQL on every engine. #}

{# Whole days from a to b (b - a) #}
{% macro days_between(a, b) -%}
    {{ return(adapter.dispatch('days_between')(a, b)) }}
{%- endmacro %}
{% macro default__days_between(a, b) -%} date_diff('day', {{ a }}, {{ b }}) {%- endmacro %}
{% macro spark__days_between(a, b) -%} datediff({{ b }}, {{ a }}) {%- endmacro %}

{# Date plus n days #}
{% macro dateadd_days(d, n) -%}
    {{ return(adapter.dispatch('dateadd_days')(d, n)) }}
{%- endmacro %}
{% macro default__dateadd_days(d, n) -%} cast({{ d }} + to_days({{ n }}) as date) {%- endmacro %}
{% macro spark__dateadd_days(d, n) -%} date_add({{ d }}, {{ n }}) {%- endmacro %}

{# Calendar years from a to b (year boundaries crossed) #}
{% macro years_between(a, b) -%}
    {{ return(adapter.dispatch('years_between')(a, b)) }}
{%- endmacro %}
{% macro default__years_between(a, b) -%} date_diff('year', {{ a }}, {{ b }}) {%- endmacro %}
{% macro spark__years_between(a, b) -%} (year({{ b }}) - year({{ a }})) {%- endmacro %}

{# First day of the month, as a DATE (Spark's date_trunc returns a timestamp) #}
{% macro month_start(d) -%}
    {{ return(adapter.dispatch('month_start')(d)) }}
{%- endmacro %}
{% macro default__month_start(d) -%} date_trunc('month', {{ d }}) {%- endmacro %}
{% macro spark__month_start(d) -%} trunc({{ d }}, 'MM') {%- endmacro %}

{# True when the text contains a match for the pattern (anchor with ^...$ for a whole-value match) #}
{% macro regex_contains(col, pattern) -%}
    {{ return(adapter.dispatch('regex_contains')(col, pattern)) }}
{%- endmacro %}
{% macro default__regex_contains(col, pattern) -%} regexp_matches({{ col }}, '{{ pattern }}') {%- endmacro %}
{% macro spark__regex_contains(col, pattern) -%} ({{ col }} rlike '{{ pattern }}') {%- endmacro %}

{# Remove Czech/Slovak diacritics: 'Dvořák' -> 'Dvorak' #}
{% macro strip_accents(col) -%}
    {{ return(adapter.dispatch('strip_accents')(col)) }}
{%- endmacro %}
{% macro default__strip_accents(col) -%} strip_accents({{ col }}) {%- endmacro %}
{% macro spark__strip_accents(col) -%}
    translate({{ col }}, 'áäčďéěíĺľňóôöŕřšťúůüýžÁÄČĎÉĚÍĹĽŇÓÔÖŔŘŠŤÚŮÜÝŽ', 'aacdeeillnooorrstuuuyzAACDEEILLNOOORRSTUUUYZ')
{%- endmacro %}

{# Sorted distinct list of values in a group #}
{% macro sorted_distinct_list(col) -%}
    {{ return(adapter.dispatch('sorted_distinct_list')(col)) }}
{%- endmacro %}
{% macro default__sorted_distinct_list(col) -%} list(distinct {{ col }} order by {{ col }}) {%- endmacro %}
{% macro spark__sorted_distinct_list(col) -%} array_sort(collect_set({{ col }})) {%- endmacro %}

{# Text value at a JSON path in a JSON-text column: json_text('subject', '$.sidlo.kodKraje') #}
{% macro json_text(col, path) -%}
    {{ return(adapter.dispatch('json_text')(col, path)) }}
{%- endmacro %}
{% macro default__json_text(col, path) -%} json_extract_string({{ col }}, '{{ path }}') {%- endmacro %}
{% macro spark__json_text(col, path) -%} get_json_object({{ col }}, '{{ path }}') {%- endmacro %}

{# Czech formats: dates 'dd.mm.yyyy', decimals '6,304' #}
{% macro cz_date(col) -%}
    {{ return(adapter.dispatch('cz_date')(col)) }}
{%- endmacro %}
{% macro default__cz_date(col) -%} cast(try_strptime(nullif(trim({{ col }}), ''), '%d.%m.%Y') as date) {%- endmacro %}
{% macro spark__cz_date(col) -%} cast(try_to_timestamp(nullif(trim({{ col }}), ''), 'dd.MM.yyyy') as date) {%- endmacro %}

{% macro cz_number(col) -%}
    try_cast(replace(replace(trim({{ col }}), ' ', ''), ',', '.') as decimal(18, 4))
{%- endmacro %}

{# IČO (Czech company ID) check digit, mod 11: weights 8..2 on the first 7 digits,
   check = (11 - sum mod 11) mod 10. Expects an 8-digit string. Same arithmetic on every engine. #}
{% macro ico_checksum_ok(col) -%}
    (
      (11 - (  8 * cast(substr({{ col }}, 1, 1) as int) + 7 * cast(substr({{ col }}, 2, 1) as int)
             + 6 * cast(substr({{ col }}, 3, 1) as int) + 5 * cast(substr({{ col }}, 4, 1) as int)
             + 4 * cast(substr({{ col }}, 5, 1) as int) + 3 * cast(substr({{ col }}, 6, 1) as int)
             + 2 * cast(substr({{ col }}, 7, 1) as int)) % 11) % 10
      = cast(substr({{ col }}, 8, 1) as int)
    )
{%- endmacro %}
