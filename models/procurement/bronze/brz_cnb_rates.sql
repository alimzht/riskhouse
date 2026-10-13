-- ČNB daily exchange rates as published: Czech dates and decimals, quoted per unit (1 EUR, 100 HUF).
select * from {{ landing_parquet('cnb_rates') }}
