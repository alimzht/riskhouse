-- freMTPL2 claim amounts as published (OpenML 41215), one row per claim, EUR.
select * from {{ landing_parquet('motor_claims') }}
