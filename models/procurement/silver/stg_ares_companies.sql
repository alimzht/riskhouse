-- What the business register says about each IČO we asked for. Rules T-S01..T-S03.
with live as (
    select
        ico,
        found,
        {{ json_text('subject', '$.obchodniJmeno') }}                         as registered_name,
        try_cast({{ json_text('subject', '$.datumVzniku') }} as date)          as founded_date,
        try_cast({{ json_text('subject', '$.datumZaniku') }} as date)          as dissolved_date,
        {{ json_text('subject', '$.pravniForma') }}                           as legal_form_code,
        {{ json_text('subject', '$.sidlo.nazevKraje') }}                      as region,
        {{ json_text('subject', '$.czNace[0]') }}                             as nace_code
    from {{ ref('brz_ares_companies') }}
),
-- T-S03 the live search does not return deleted companies; the commercial register still knows them
deleted as (
    select
        ico,
        {{ json_text('record', '$.zaznamy[0].obchodniJmeno[0].hodnota') }}            as registered_name,
        try_cast({{ json_text('record', '$.zaznamy[0].datumZapisu') }} as date)        as founded_date,
        try_cast({{ json_text('record', '$.zaznamy[0].datumVymazu') }} as date)        as deleted_date
    from {{ ref('brz_ares_deleted') }}
    where found
),
buyers as (select distinct buyer_ico as ico from {{ ref('stg_contracts') }})
select
    l.ico,
    l.found or d.ico is not null                                           as found_in_ares,
    coalesce(l.registered_name, d.registered_name)                         as registered_name,
    coalesce(l.founded_date, d.founded_date)                               as founded_date,
    coalesce(l.dissolved_date, d.deleted_date)                             as dissolved_date,
    l.legal_form_code,
    l.region,
    l.nace_code,
    -- T-S01 'v likvidaci' (in liquidation) is part of the registered name while a company is being wound up
    coalesce(lower(coalesce(l.registered_name, d.registered_name)) like '%v likvidaci%', false) as in_liquidation,
    -- T-S02 public body: it publishes contracts itself (it is a buyer in the register), or its legal form is
    -- organizační složka státu (325), příspěvková organizace (331), obec (801) or kraj (804)
    (b.ico is not null or coalesce(l.legal_form_code in ('325', '331', '801', '804'), false)) as is_public_body
from live l
left join deleted d on d.ico = l.ico
left join buyers b on b.ico = l.ico
