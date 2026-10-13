-- One row per contract: its latest published version, typed, value in CZK excl. VAT, type classified.
-- Rules T-V01..T-V06, see docs/transformation_rules.md.

{#- T-V05 construction work is recognised from the free-text subject (the register has no type field) -#}
{%- set is_construction = regex_contains(strip_accents('lower(subject)'),
        'stavb|staveb|rekonstrukc|vystavb|zateplen|demolic|sanac|stavebni prace') %}

with versions as (
    select
        *,
        -- T-V01 a contract can be republished many times; the highest version id is the current one
        row_number() over (partition by contract_id order by cast(version_id as bigint) desc) as version_rank,
        count(*) over (partition by contract_id)                                              as n_versions
    from {{ ref('brz_contracts') }}
),
latest as (
    select * from versions
    where version_rank = 1
      and is_valid_record = '1'        -- T-V02 latest version withdrawn (platnyZaznam = 0): contract no longer valid
),
typed as (
    select
        contract_id,
        version_id,
        url,
        n_versions,
        try_cast(left(published_at, 10) as date)                 as published_date,
        try_cast(signed_date as date)                            as signed_date_raw,
        trim(subject)                                            as subject,
        trim(buyer_ico)                                          as buyer_ico,
        trim(buyer_name)                                         as buyer_name,
        try_cast(value_excl_vat as decimal(18, 2))               as value_excl_vat,
        try_cast(value_incl_vat as decimal(18, 2))               as value_incl_vat,
        try_cast(foreign_value as decimal(18, 2))                as foreign_value,
        upper(trim(foreign_currency))                            as foreign_currency,
        price_not_stated_reason is not null                      as price_not_stated
    from latest
),
dated as (
    select
        *,
        -- T-V06 a contract is signed before it is published, and not before 2000: anything else is a typo
        -- (seen: year 0001, 2926) -> unknown, so it cannot distort the date rules R1/R6
        case when signed_date_raw between date '2000-01-01' and published_date then signed_date_raw end as signed_date,
        signed_date_raw is not null
          and not (signed_date_raw between date '2000-01-01' and published_date)                       as dq_implausible_signed_date
    from typed
),
-- T-V04 foreign currency: ČNB rate of the signing day, or the last trading day before it
fx as (
    select t.contract_id, r.czk_per_unit,
           row_number() over (partition by t.contract_id order by r.rate_date desc) as rn
    from dated t
    join {{ ref('stg_cnb_rates') }} r
      on r.currency = t.foreign_currency
     and r.rate_date <= coalesce(t.signed_date, t.published_date)
     and r.rate_date >= {{ dateadd_days('coalesce(t.signed_date, t.published_date)', -10) }}
),
valued as (
    select
        t.*,
        -- T-V03 value in CZK excl. VAT: stated excl. VAT > incl. VAT / 1.21 (estimated) > foreign currency at ČNB rate
        case
            when t.value_excl_vat is not null then t.value_excl_vat
            when t.value_incl_vat is not null then round(t.value_incl_vat / (1 + {{ var('vat_rate') }}), 2)
            when t.foreign_value  is not null then round(t.foreign_value * fx.czk_per_unit, 2)
        end as value_czk,
        case
            when t.value_excl_vat is not null then 'excl_vat'
            when t.value_incl_vat is not null then 'incl_vat_estimated'
            when t.foreign_value is not null and fx.czk_per_unit is not null then 'foreign_currency'
            when t.foreign_value is not null then 'foreign_currency_no_rate'
            else 'not_stated'
        end as value_basis
    from dated t
    left join fx on fx.contract_id = t.contract_id and fx.rn = 1
)
select
    *,
    -- T-V05 construction work has a higher tender limit than supplies and services
    case when {{ is_construction }} then 'construction' else 'supplies_services' end    as contract_type,
    case when {{ is_construction }} then {{ var('tender_limit_construction') }}
         else {{ var('tender_limit_supplies_services') }} end                          as tender_limit_czk
from valued
