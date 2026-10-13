-- Every valid IČO on a contract must have an ARES answer. Without one, R1/R2/R4 cannot fire and the contract
-- would be auto-cleared silently, e.g. after an interrupted `ingest/lookup_ares.py`. Fix: re-run it.
select distinct p.party_ico
from {{ ref('stg_contract_parties') }} p
left join {{ ref('stg_ares_companies') }} a on a.ico = p.party_ico
where p.ico_status = 'valid' and a.ico is null
