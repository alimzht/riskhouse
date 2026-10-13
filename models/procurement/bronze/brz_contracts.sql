-- Bronze = landing as-is: one row per published record (a contract version), every value text.
select * from {{ landing_parquet('contracts') }}
