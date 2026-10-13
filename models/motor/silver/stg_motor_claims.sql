-- Claim cost per policy. Rule T-M03: single claims above the large-claim threshold are capped, so one
-- catastrophic claim does not decide a whole segment's price (the excess is reported separately).
with claims as (
    select cast(cast(IDpol as double) as bigint)   as policy_id,
           cast(ClaimAmount as double)             as amount_eur
    from {{ ref('brz_motor_claims') }}
)
select
    policy_id,
    count(*)                                                                    as n_claim_records,
    sum(amount_eur)                                                             as claim_cost_eur,
    sum(least(amount_eur, {{ var('motor_large_claim_eur') }}))                   as claim_cost_capped_eur,
    sum(case when amount_eur > {{ var('motor_large_claim_eur') }} then 1 else 0 end) as n_large_claims
from claims
group by policy_id
