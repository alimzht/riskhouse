-- freMTPL2 policies as published (OpenML 41214), every value text.
select * from {{ landing_parquet('motor_policies') }}
