-- T-F01 ČNB rates to CZK per 1 unit of currency ('100 HUF = 6,304' -> 0.06304), typed.
select
    {{ cz_date('rate_date') }}                                  as rate_date,
    upper(trim(currency))                                       as currency,
    {{ cz_number('rate') }} / cast(unit as int)                 as czk_per_unit
from {{ ref('brz_cnb_rates') }}
where {{ cz_number('rate') }} is not null
