-- What ARES (the business register) says about each IČO we asked for. Rules T-S01..T-S03.
with ares as (
    select
        ico,
        found                                                                 as found_in_ares,
        {{ json_text('subject', '$.obchodniJmeno') }}                         as registered_name,
        try_cast({{ json_text('subject', '$.datumVzniku') }} as date)          as founded_date,
        try_cast({{ json_text('subject', '$.datumZaniku') }} as date)          as dissolved_date,
        {{ json_text('subject', '$.pravniForma') }}                           as legal_form_code,
        {{ json_text('subject', '$.sidlo.nazevKraje') }}                      as region,
        {{ json_text('subject', '$.czNace[0]') }}                             as nace_code
    from {{ ref('brz_ares_companies') }}
),
buyers as (select distinct buyer_ico as ico from {{ ref('stg_contracts') }})
select
    a.*,
    -- T-S01 'v likvidaci' (in liquidation) is part of the registered name while a company is being wound up
    coalesce(lower(a.registered_name) like '%v likvidaci%', false)          as in_liquidation,
    -- T-S02 public body: it publishes contracts itself (it is a buyer in the register), or its legal form is
    -- organizační složka státu (325), příspěvková organizace (331), obec (801) or kraj (804)
    (b.ico is not null or coalesce(a.legal_form_code in ('325', '331', '801', '804'), false)) as is_public_body
from ares a
left join buyers b on b.ico = a.ico
