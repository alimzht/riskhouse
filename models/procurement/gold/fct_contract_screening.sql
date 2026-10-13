-- One row per contract x counterparty, with risk flags R1..R6 and the review decision.
-- A flag is a reason for a person to look closer, not a finding of wrongdoing. Rules: docs/transformation_rules.md;
-- thresholds: dbt_project.yml vars.
with base as (
    select
        c.contract_id, c.version_id, c.url, c.signed_date, c.published_date, c.subject,
        c.buyer_ico, c.buyer_name, c.value_czk, c.value_basis, c.contract_type, c.tender_limit_czk,
        p.party_seq, p.party_name, p.party_ico, p.ico_status, p.is_natural_person, p.is_foreign,
        s.found_in_ares      as in_register,
        s.registered_name, s.founded_date, s.dissolved_date, s.in_liquidation, s.region, s.nace_code,
        coalesce(s.is_public_body, false) as supplier_is_public_body,
        -- a company is expected to have a valid Czech IČO; individuals and foreign suppliers are not
        not (p.is_natural_person or p.is_foreign)                          as expects_czech_ico
    from {{ ref('stg_contracts') }} c
    join {{ ref('stg_contract_parties') }} p on p.version_id = c.version_id
    left join {{ ref('stg_ares_companies') }} s on s.ico = p.party_ico
),
-- R6 contract splitting: same buyer and supplier, other contracts within the window, each below the limit
-- but together above it
pairs as (
    select a.contract_id, a.party_seq,
           count(distinct b.contract_id)  as pair_contracts_in_window,
           sum(b.value_czk)               as pair_value_in_window
    from base a
    join base b
      on b.buyer_ico = a.buyer_ico and b.party_ico = a.party_ico
     and abs({{ days_between('a.signed_date', 'b.signed_date') }}) <= {{ var('split_window_days') }}
     and b.value_czk < b.tender_limit_czk
    where a.party_ico is not null and a.value_czk < a.tender_limit_czk
    group by a.contract_id, a.party_seq
),
flags as (
    select
        b.*,
        pr.pair_contracts_in_window,
        pr.pair_value_in_window,
        -- R1 supplier founded less than ~6 months before signing (or after it). Public bodies have no founding date.
        coalesce({{ days_between('b.founded_date', 'b.signed_date') }} < {{ var('new_company_days') }}
                 and not b.supplier_is_public_body, false)                                       as r1_new_company,
        -- R2 supplier dissolved before signing, or in liquidation
        coalesce(b.dissolved_date <= b.signed_date, false) or coalesce(b.in_liquidation, false)  as r2_dissolved,
        -- R3 a company without a valid IČO: missing, malformed or failing the check digit
        b.expects_czech_ico and b.ico_status <> 'valid'                                          as r3_invalid_ico,
        -- R4 valid-looking IČO that the business register does not know
        b.expects_czech_ico and b.ico_status = 'valid' and coalesce(not b.in_register, false)    as r4_not_in_register,
        -- R5 value just under the tender limit: CHECKPOINT 1, written by Tim (see docs/checkpoints.md)
        false                                                                                    as r5_near_limit,
        -- R6 several contracts with the same buyer within the window, each under the limit, together over it
        coalesce(pr.pair_contracts_in_window >= 2 and pr.pair_value_in_window > b.tender_limit_czk, false)
                                                                                                 as r6_split
    from base b
    left join pairs pr on pr.contract_id = b.contract_id and pr.party_seq = b.party_seq
)
select
    *,
    cast(r1_new_company as int) + cast(r2_dissolved as int) + cast(r3_invalid_ico as int)
      + cast(r4_not_in_register as int) + cast(r5_near_limit as int) + cast(r6_split as int)    as n_flags,
    case when r1_new_company or r2_dissolved or r3_invalid_ico or r4_not_in_register or r5_near_limit or r6_split
         then 'review' else 'auto_clear' end                                                     as review_queue
from flags
