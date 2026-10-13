-- T-F01 ČNB rates to CZK per 1 unit of currency ('100 HUF = 6,304' -> 0.06304), typed.
select
    {{ cz_date('rate_date') }}                                  as rate_date,
    upper(trim(currency))                                       as currency,
    -- exact per-unit rate: multiply instead of divide, so no engine turns it into a float
    {{ cz_number('rate') }} * case cast(unit as int) when 1 then 1 when 100 then 0.01 when 1000 then 0.001 end
                                                                as czk_per_unit
from {{ ref('brz_cnb_rates') }}
where {{ cz_number('rate') }} is not null
