-- Motor policies typed, cleaned and banded into rating segments. Rules T-M01, T-M02, T-M04.
with typed as (
    select
        cast(cast(IDpol as double) as bigint)   as policy_id,
        cast(cast(ClaimNb as double) as int)    as claim_nb_raw,
        cast(Exposure as double)                as exposure_raw,
        trim(Area)                              as area,
        cast(cast(VehPower as double) as int)   as veh_power,
        cast(cast(VehAge as double) as int)     as veh_age,
        cast(cast(DrivAge as double) as int)    as driver_age,
        cast(cast(BonusMalus as double) as int) as bonus_malus,
        trim(VehBrand)                          as veh_brand,
        trim(VehGas)                            as veh_gas,
        cast(cast(Density as double) as int)    as density,
        trim(Region)                            as region
    from {{ ref('brz_motor_policies') }}
)
select
    policy_id,
    claim_nb_raw,
    -- T-M01 exposure is years insured in the period; values above 1 are data errors -> capped at 1 year
    least(exposure_raw, 1.0)                                       as exposure,
    exposure_raw > 1.0                                             as dq_exposure_capped,
    -- T-M02 more than 4 claims on one policy in a year is implausible for private motor -> capped at 4
    least(claim_nb_raw, 4)                                         as claim_nb,
    claim_nb_raw > 4                                               as dq_claims_capped,
    area, veh_power, veh_age, driver_age, bonus_malus, veh_brand, veh_gas, density, region,
    -- T-M04 rating bands, the way a tariff groups customers
    case when driver_age < 21 then '18-20' when driver_age < 26 then '21-25' when driver_age < 31 then '26-30'
         when driver_age < 41 then '31-40' when driver_age < 51 then '41-50' when driver_age < 61 then '51-60'
         when driver_age < 71 then '61-70' else '71+' end          as driver_age_band,
    case when veh_age < 1 then '0' when veh_age < 4 then '1-3' when veh_age < 8 then '4-7'
         when veh_age < 13 then '8-12' else '13+' end              as veh_age_band,
    case when veh_power <= 5 then '4-5' when veh_power <= 7 then '6-7' when veh_power <= 9 then '8-9'
         else '10+' end                                            as veh_power_band,
    case when bonus_malus = 50 then '50 (best)' when bonus_malus < 80 then '51-79' when bonus_malus < 100 then '80-99'
         when bonus_malus < 125 then '100-124' else '125+ (malus)' end as bonus_malus_band,
    case when density < 50 then '<50' when density < 200 then '50-199' when density < 1000 then '200-999'
         when density < 5000 then '1000-4999' else '5000+' end     as density_band
from typed
