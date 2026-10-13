-- One row per counterparty (smluvniStrana) of a contract version, as published.
select * from {{ landing_parquet('contract_parties') }}
