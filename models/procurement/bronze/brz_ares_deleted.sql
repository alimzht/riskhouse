-- Commercial-register answers for IČOs the live ARES search did not know: deleted companies, with
-- their deletion date. `record` is the raw JSON answer, NULL when the register does not know the IČO either.
select * from {{ landing('ares_deleted',
    "read_json('" ~ var('landing_path') ~ "/ares_deleted.jsonl', format='newline_delimited',
               columns={ico:'varchar', found:'boolean', fetched_at:'varchar', record:'json'})") }}
