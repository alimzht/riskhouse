-- ARES (business register) answers, one row per IČO asked; `subject` is the raw JSON answer, NULL when not found.
select * from {{ landing('ares_raw',
    "read_json('" ~ var('landing_path') ~ "/ares_raw.jsonl', format='newline_delimited',
               columns={ico:'varchar', found:'boolean', fetched_at:'varchar', subject:'json'})") }}
