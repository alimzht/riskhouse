-- Counterparties of each current contract version, with the IČO (company ID) normalised and validated.
-- Rules T-P01..T-P04, see docs/transformation_rules.md.
with parties as (
    select
        p.version_id,
        cast(p.party_seq as int)                                   as party_seq,
        trim(p.party_name)                                         as party_name,
        trim(p.party_address)                                      as party_address,
        replace(coalesce(p.party_ico, ''), ' ', '')                as ico_raw,
        coalesce(p.party_kind = 'FO', false)                       as is_natural_person,   -- T-P01 FO = fyzická osoba
        coalesce(p.party_is_recipient = '1', false)                as is_recipient
    from {{ ref('brz_contract_parties') }} p
    join {{ ref('stg_contracts') }} c on c.version_id = p.version_id      -- current versions only
)
select
    version_id,
    party_seq,
    party_name,
    party_address,
    is_natural_person,
    is_recipient,
    -- T-P02 IČO is 8 digits; published without leading zeros it is padded ('6947' -> '00006947')
    case when {{ regex_full_match('ico_raw', '^[0-9]{1,8}$') }} then lpad(ico_raw, 8, '0') end   as party_ico,
    case
        when ico_raw = ''                                          then 'missing'
        when not {{ regex_full_match('ico_raw', '^[0-9]{1,8}$') }} then 'malformed'
        when not {{ ico_checksum_ok("lpad(ico_raw, 8, '0')") }}    then 'checksum_failed'   -- T-P03
        else 'valid'
    end                                                                                          as ico_status,
    -- T-P04 foreign suppliers legitimately have no Czech IČO; recognised by the country in their address
    {{ regex_full_match(strip_accents("lower(coalesce(party_address, ''))"),
       'slovak|slovensk|nemecko|deutschland|germany|rakousko|austria|osterreich|polsk|poland|irsko|ireland|'
       ~ 'nizozemsk|netherlands|usa|united states|united kingdom|velka britanie|francie|france|madarsk|hungary|'
       ~ 'svycarsk|switzerland|schweiz|belgi|lucembursk|luxembourg|italie|italy|spanelsk|spain|dansk|denmark|svedsk|sweden') }}
                                                                                                 as is_foreign
from parties
