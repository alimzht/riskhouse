-- One row per policy-year: exposure, claims and claim cost, with its rating segments.
select
    p.*,
    coalesce(c.claim_cost_eur, 0)          as claim_cost_eur,
    coalesce(c.claim_cost_capped_eur, 0)   as claim_cost_capped_eur,
    coalesce(c.n_claim_records, 0)         as n_claim_records,
    coalesce(c.n_large_claims, 0)          as n_large_claims,
    -- T-M05 claim count and claim amounts come from two files that do not always agree
    p.claim_nb_raw > 0 and c.policy_id is null as dq_claims_without_amount
from {{ ref('stg_motor_policies') }} p
left join {{ ref('stg_motor_claims') }} c using (policy_id)
