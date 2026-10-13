-- Expected claim cost by rating segment, and who would pay for whom under one flat price.
-- frequency = claims per policy-year; severity = cost per claim; pure premium = cost per policy-year (capped claims);
-- relativity = segment pure premium / portfolio pure premium (1.30 = 30 % more expensive than average);
-- flat_price_gap_eur > 0: under one price for everybody this segment pays more than it costs (subsidises others).
{% set factors = [('Driver age', 'driver_age_band'), ('Bonus-malus', 'bonus_malus_band'),
                  ('Vehicle power', 'veh_power_band'), ('Vehicle age', 'veh_age_band'),
                  ('Population density', 'density_band'), ('Area', 'area'), ('Fuel', 'veh_gas')] %}
with portfolio as (
    select sum(claim_cost_capped_eur) / sum(exposure) as portfolio_pure_premium from {{ ref('fct_motor_policy') }}
),
segments as (
{% for label, col in factors %}
    select '{{ label }}' as factor, cast({{ col }} as string) as segment,
           count(*) as policies, sum(exposure) as exposure_years,
           sum(claim_nb) as claims, sum(claim_cost_capped_eur) as claim_cost_eur
    from {{ ref('fct_motor_policy') }}
    group by {{ col }}
    {% if not loop.last %}union all{% endif %}
{% endfor %}
)
select
    s.factor, s.segment, s.policies,
    round(s.exposure_years, 1)                                                   as exposure_years,
    s.claims,
    round(s.claims / s.exposure_years, 4)                                        as frequency,
    round(s.claim_cost_eur / nullif(s.claims, 0), 0)                             as severity_eur,
    round(s.claim_cost_eur / s.exposure_years, 2)                                as pure_premium_eur,
    round(s.claim_cost_eur / s.exposure_years / p.portfolio_pure_premium, 2)     as relativity,
    round(s.exposure_years * p.portfolio_pure_premium - s.claim_cost_eur, 0)     as flat_price_gap_eur
from segments s cross join portfolio p
