window.RISKHOUSE = {
 "summary": {
  "contracts": 275570,
  "flagged": 13162,
  "first_signed": "2000-06-28",
  "last_signed": "2026-09-30",
  "auto_cleared": 262408,
  "hours_low": 21867,
  "hours_high": 65602,
  "period": "July–September 2026 (publication month)"
 },
 "rule_hits": [
  {
   "rule": "R1",
   "label": "Supplier founded < 6 months before signing",
   "contracts": 869
  },
  {
   "rule": "R2",
   "label": "Supplier dissolved or in liquidation",
   "contracts": 61
  },
  {
   "rule": "R3",
   "label": "Company without a valid IČO",
   "contracts": 7797
  },
  {
   "rule": "R4",
   "label": "IČO unknown to the business register",
   "contracts": 405
  },
  {
   "rule": "R5",
   "label": "Value just under the tender limit",
   "contracts": 1243
  },
  {
   "rule": "R6",
   "label": "Possible contract splitting",
   "contracts": 3095
  }
 ],
 "histogram": [
  {
   "bin_start": 1000000,
   "contracts": 792
  },
  {
   "bin_start": 1050000,
   "contracts": 510
  },
  {
   "bin_start": 1100000,
   "contracts": 560
  },
  {
   "bin_start": 1150000,
   "contracts": 494
  },
  {
   "bin_start": 1200000,
   "contracts": 632
  },
  {
   "bin_start": 1250000,
   "contracts": 419
  },
  {
   "bin_start": 1300000,
   "contracts": 394
  },
  {
   "bin_start": 1350000,
   "contracts": 488
  },
  {
   "bin_start": 1400000,
   "contracts": 341
  },
  {
   "bin_start": 1450000,
   "contracts": 333
  },
  {
   "bin_start": 1500000,
   "contracts": 388
  },
  {
   "bin_start": 1550000,
   "contracts": 354
  },
  {
   "bin_start": 1600000,
   "contracts": 303
  },
  {
   "bin_start": 1650000,
   "contracts": 289
  },
  {
   "bin_start": 1700000,
   "contracts": 261
  },
  {
   "bin_start": 1750000,
   "contracts": 222
  },
  {
   "bin_start": 1800000,
   "contracts": 245
  },
  {
   "bin_start": 1850000,
   "contracts": 212
  },
  {
   "bin_start": 1900000,
   "contracts": 222
  },
  {
   "bin_start": 1950000,
   "contracts": 255
  },
  {
   "bin_start": 2000000,
   "contracts": 276
  },
  {
   "bin_start": 2050000,
   "contracts": 157
  },
  {
   "bin_start": 2100000,
   "contracts": 148
  },
  {
   "bin_start": 2150000,
   "contracts": 164
  },
  {
   "bin_start": 2200000,
   "contracts": 139
  },
  {
   "bin_start": 2250000,
   "contracts": 157
  },
  {
   "bin_start": 2300000,
   "contracts": 126
  },
  {
   "bin_start": 2350000,
   "contracts": 136
  },
  {
   "bin_start": 2400000,
   "contracts": 125
  },
  {
   "bin_start": 2450000,
   "contracts": 160
  },
  {
   "bin_start": 2500000,
   "contracts": 190
  },
  {
   "bin_start": 2550000,
   "contracts": 123
  },
  {
   "bin_start": 2600000,
   "contracts": 103
  },
  {
   "bin_start": 2650000,
   "contracts": 120
  },
  {
   "bin_start": 2700000,
   "contracts": 99
  },
  {
   "bin_start": 2750000,
   "contracts": 106
  },
  {
   "bin_start": 2800000,
   "contracts": 113
  },
  {
   "bin_start": 2850000,
   "contracts": 137
  },
  {
   "bin_start": 2900000,
   "contracts": 134
  },
  {
   "bin_start": 2950000,
   "contracts": 213
  }
 ],
 "data_quality": [
  {
   "entity": "contracts",
   "check_name": "older versions superseded by a newer one",
   "records": 6563,
   "action_taken": "kept the latest version only (T-V01)"
  },
  {
   "entity": "contracts",
   "check_name": "latest version withdrawn (platnyZaznam = 0)",
   "records": 524,
   "action_taken": "excluded (T-V02)"
  },
  {
   "entity": "contracts",
   "check_name": "impossible signing date (before 2000 or after publication)",
   "records": 397,
   "action_taken": "set to unknown, excluded from date rules (T-V06)"
  },
  {
   "entity": "contracts",
   "check_name": "value only stated incl. VAT",
   "records": 48486,
   "action_taken": "divided by 1.21, marked estimated (T-V03)"
  },
  {
   "entity": "contracts",
   "check_name": "value in foreign currency",
   "records": 3495,
   "action_taken": "converted at the ČNB rate of the signing day, or the last trading day up to 10 days before (T-V04)"
  },
  {
   "entity": "contracts",
   "check_name": "value in foreign currency with no ČNB rate",
   "records": 1,
   "action_taken": "value left unknown, excluded from value rules R5/R6 (T-V04)"
  },
  {
   "entity": "contracts",
   "check_name": "no value stated",
   "records": 31427,
   "action_taken": "kept, excluded from value rules R5/R6"
  },
  {
   "entity": "contracts",
   "check_name": "classified as construction from the subject text",
   "records": 11701,
   "action_taken": "tender limit 6,000,000 CZK instead of 2,000,000 (T-V05)"
  },
  {
   "entity": "counterparties",
   "check_name": "natural person (no IČO expected)",
   "records": 3285,
   "action_taken": "excluded from IČO rules R3-R4 (T-P01)"
  },
  {
   "entity": "counterparties",
   "check_name": "foreign supplier (no Czech IČO expected)",
   "records": 2669,
   "action_taken": "excluded from IČO rules R3-R4 (T-P04)"
  },
  {
   "entity": "counterparties",
   "check_name": "IČO published without leading zeros",
   "records": 832,
   "action_taken": "padded to 8 digits (T-P02)"
  },
  {
   "entity": "counterparties",
   "check_name": "IČO missing (company expected)",
   "records": 7475,
   "action_taken": "flagged R3"
  },
  {
   "entity": "counterparties",
   "check_name": "IČO malformed or failing the check digit",
   "records": 977,
   "action_taken": "flagged R3 (T-P03)"
  },
  {
   "entity": "counterparties",
   "check_name": "valid IČO unknown to the business register",
   "records": 412,
   "action_taken": "flagged R4"
  }
 ],
 "motor": [
  {
   "factor": "Area",
   "segment": "A",
   "policies": 103957,
   "exposure_years": 61956.8,
   "claims": 5056,
   "frequency": 0.0816,
   "severity_eur": 1325.0,
   "pure_premium_eur": 108.13,
   "relativity": 0.79
  },
  {
   "factor": "Area",
   "segment": "B",
   "policies": 75459,
   "exposure_years": 43001.8,
   "claims": 3800,
   "frequency": 0.0884,
   "severity_eur": 1252.0,
   "pure_premium_eur": 110.63,
   "relativity": 0.8
  },
  {
   "factor": "Area",
   "segment": "C",
   "policies": 191880,
   "exposure_years": 104402.5,
   "claims": 9875,
   "frequency": 0.0946,
   "severity_eur": 1280.0,
   "pure_premium_eur": 121.06,
   "relativity": 0.88
  },
  {
   "factor": "Area",
   "segment": "D",
   "policies": 151596,
   "exposure_years": 77087.8,
   "claims": 8390,
   "frequency": 0.1088,
   "severity_eur": 1467.0,
   "pure_premium_eur": 159.64,
   "relativity": 1.16
  },
  {
   "factor": "Area",
   "segment": "E",
   "policies": 137167,
   "exposure_years": 63785.7,
   "claims": 7804,
   "frequency": 0.1223,
   "severity_eur": 1504.0,
   "pure_premium_eur": 183.99,
   "relativity": 1.34
  },
  {
   "factor": "Area",
   "segment": "F",
   "policies": 17954,
   "exposure_years": 8125.4,
   "claims": 1131,
   "frequency": 0.1392,
   "severity_eur": 1030.0,
   "pure_premium_eur": 143.36,
   "relativity": 1.04
  },
  {
   "factor": "Bonus-malus",
   "segment": "100-124",
   "policies": 25099,
   "exposure_years": 8820.1,
   "claims": 2598,
   "frequency": 0.2946,
   "severity_eur": 1898.0,
   "pure_premium_eur": 559.01,
   "relativity": 4.06
  },
  {
   "factor": "Bonus-malus",
   "segment": "125+ (malus)",
   "policies": 2225,
   "exposure_years": 991.1,
   "claims": 465,
   "frequency": 0.4692,
   "severity_eur": 1896.0,
   "pure_premium_eur": 889.7,
   "relativity": 6.47
  },
  {
   "factor": "Bonus-malus",
   "segment": "50 (best)",
   "policies": 384156,
   "exposure_years": 225152.7,
   "claims": 18010,
   "frequency": 0.08,
   "severity_eur": 1150.0,
   "pure_premium_eur": 91.99,
   "relativity": 0.67
  },
  {
   "factor": "Bonus-malus",
   "segment": "51-79",
   "policies": 195115,
   "exposure_years": 93586.7,
   "claims": 10718,
   "frequency": 0.1145,
   "severity_eur": 1517.0,
   "pure_premium_eur": 173.74,
   "relativity": 1.26
  },
  {
   "factor": "Bonus-malus",
   "segment": "80-99",
   "policies": 71418,
   "exposure_years": 29809.5,
   "claims": 4265,
   "frequency": 0.1431,
   "severity_eur": 1528.0,
   "pure_premium_eur": 218.68,
   "relativity": 1.59
  },
  {
   "factor": "Driver age",
   "segment": "18-20",
   "policies": 6816,
   "exposure_years": 2584.5,
   "claims": 643,
   "frequency": 0.2488,
   "severity_eur": 2783.0,
   "pure_premium_eur": 692.35,
   "relativity": 5.03
  },
  {
   "factor": "Driver age",
   "segment": "21-25",
   "policies": 32079,
   "exposure_years": 13642.7,
   "claims": 2198,
   "frequency": 0.1611,
   "severity_eur": 1600.0,
   "pure_premium_eur": 257.8,
   "relativity": 1.87
  },
  {
   "factor": "Driver age",
   "segment": "26-30",
   "policies": 65594,
   "exposure_years": 29167.2,
   "claims": 3093,
   "frequency": 0.106,
   "severity_eur": 1417.0,
   "pure_premium_eur": 150.29,
   "relativity": 1.09
  },
  {
   "factor": "Driver age",
   "segment": "31-40",
   "policies": 170097,
   "exposure_years": 83897.5,
   "claims": 7522,
   "frequency": 0.0897,
   "severity_eur": 1452.0,
   "pure_premium_eur": 130.21,
   "relativity": 0.95
  },
  {
   "factor": "Driver age",
   "segment": "41-50",
   "policies": 165185,
   "exposure_years": 88100.0,
   "claims": 9165,
   "frequency": 0.104,
   "severity_eur": 1246.0,
   "pure_premium_eur": 129.58,
   "relativity": 0.94
  },
  {
   "factor": "Driver age",
   "segment": "51-60",
   "policies": 135014,
   "exposure_years": 75700.4,
   "claims": 7254,
   "frequency": 0.0958,
   "severity_eur": 1295.0,
   "pure_premium_eur": 124.13,
   "relativity": 0.9
  },
  {
   "factor": "Driver age",
   "segment": "61-70",
   "policies": 63863,
   "exposure_years": 38321.2,
   "claims": 3558,
   "frequency": 0.0928,
   "severity_eur": 1161.0,
   "pure_premium_eur": 107.79,
   "relativity": 0.78
  },
  {
   "factor": "Driver age",
   "segment": "71+",
   "policies": 39365,
   "exposure_years": 26946.6,
   "claims": 2623,
   "frequency": 0.0973,
   "severity_eur": 1428.0,
   "pure_premium_eur": 138.97,
   "relativity": 1.01
  },
  {
   "factor": "Fuel",
   "segment": "Diesel",
   "policies": 332136,
   "exposure_years": 170587.6,
   "claims": 16640,
   "frequency": 0.0975,
   "severity_eur": 1495.0,
   "pure_premium_eur": 145.8,
   "relativity": 1.06
  },
  {
   "factor": "Fuel",
   "segment": "Regular",
   "policies": 345877,
   "exposure_years": 187772.6,
   "claims": 19416,
   "frequency": 0.1034,
   "severity_eur": 1258.0,
   "pure_premium_eur": 130.11,
   "relativity": 0.95
  },
  {
   "factor": "Population density",
   "segment": "1000-4999",
   "policies": 184757,
   "exposure_years": 89925.4,
   "claims": 10434,
   "frequency": 0.116,
   "severity_eur": 1522.0,
   "pure_premium_eur": 176.55,
   "relativity": 1.28
  },
  {
   "factor": "Population density",
   "segment": "200-999",
   "policies": 183523,
   "exposure_years": 96852.2,
   "claims": 9776,
   "frequency": 0.1009,
   "severity_eur": 1354.0,
   "pure_premium_eur": 136.68,
   "relativity": 0.99
  },
  {
   "factor": "Population density",
   "segment": "50-199",
   "policies": 157306,
   "exposure_years": 87864.0,
   "claims": 7904,
   "frequency": 0.09,
   "severity_eur": 1246.0,
   "pure_premium_eur": 112.1,
   "relativity": 0.81
  },
  {
   "factor": "Population density",
   "segment": "5000+",
   "policies": 49384,
   "exposure_years": 22258.0,
   "claims": 2947,
   "frequency": 0.1324,
   "severity_eur": 1266.0,
   "pure_premium_eur": 167.56,
   "relativity": 1.22
  },
  {
   "factor": "Population density",
   "segment": "<50",
   "policies": 103043,
   "exposure_years": 61460.4,
   "claims": 4995,
   "frequency": 0.0813,
   "severity_eur": 1323.0,
   "pure_premium_eur": 107.53,
   "relativity": 0.78
  },
  {
   "factor": "Vehicle age",
   "segment": "0",
   "policies": 57739,
   "exposure_years": 16696.3,
   "claims": 5205,
   "frequency": 0.3117,
   "severity_eur": 451.0,
   "pure_premium_eur": 140.45,
   "relativity": 1.02
  },
  {
   "factor": "Vehicle age",
   "segment": "1-3",
   "policies": 180669,
   "exposure_years": 88517.2,
   "claims": 8019,
   "frequency": 0.0906,
   "severity_eur": 1542.0,
   "pure_premium_eur": 139.68,
   "relativity": 1.02
  },
  {
   "factor": "Vehicle age",
   "segment": "13+",
   "policies": 127288,
   "exposure_years": 73384.4,
   "claims": 5313,
   "frequency": 0.0724,
   "severity_eur": 1614.0,
   "pure_premium_eur": 116.82,
   "relativity": 0.85
  },
  {
   "factor": "Vehicle age",
   "segment": "4-7",
   "policies": 150826,
   "exposure_years": 85974.6,
   "claims": 8532,
   "frequency": 0.0992,
   "severity_eur": 1516.0,
   "pure_premium_eur": 150.48,
   "relativity": 1.09
  },
  {
   "factor": "Vehicle age",
   "segment": "8-12",
   "policies": 161491,
   "exposure_years": 93787.5,
   "claims": 8987,
   "frequency": 0.0958,
   "severity_eur": 1456.0,
   "pure_premium_eur": 139.49,
   "relativity": 1.01
  },
  {
   "factor": "Vehicle power",
   "segment": "10+",
   "policies": 66425,
   "exposure_years": 31726.7,
   "claims": 3441,
   "frequency": 0.1085,
   "severity_eur": 1505.0,
   "pure_premium_eur": 163.25,
   "relativity": 1.19
  },
  {
   "factor": "Vehicle power",
   "segment": "4-5",
   "policies": 240170,
   "exposure_years": 128203.5,
   "claims": 12932,
   "frequency": 0.1009,
   "severity_eur": 1234.0,
   "pure_premium_eur": 124.51,
   "relativity": 0.9
  },
  {
   "factor": "Vehicle power",
   "segment": "6-7",
   "policies": 294377,
   "exposure_years": 160417.3,
   "claims": 16007,
   "frequency": 0.0998,
   "severity_eur": 1434.0,
   "pure_premium_eur": 143.06,
   "relativity": 1.04
  },
  {
   "factor": "Vehicle power",
   "segment": "8-9",
   "policies": 77041,
   "exposure_years": 38012.6,
   "claims": 3676,
   "frequency": 0.0967,
   "severity_eur": 1418.0,
   "pure_premium_eur": 137.09,
   "relativity": 1.0
  }
 ],
 "examples": [
  {
   "contract_id": "36790918",
   "url": "https://smlouvy.gov.cz/smlouva/39140818",
   "signed_date": "2026-08-07",
   "buyer_name": "Městská část Praha 10",
   "supplier": "EPRE Vršovická s.r.o.",
   "value_czk": "1117396694.00",
   "flags": "R1",
   "example_for": "R1"
  },
  {
   "contract_id": "1102381",
   "url": "https://smlouvy.gov.cz/smlouva/39715417",
   "signed_date": "2009-12-10",
   "buyer_name": "Armádní Servisní, příspěvková organizace",
   "supplier": "Teplárny Brno Distribuce, a.s.",
   "value_czk": "48193700.00",
   "flags": "R1",
   "example_for": "R1"
  },
  {
   "contract_id": "26882798",
   "url": "https://smlouvy.gov.cz/smlouva/39685077",
   "signed_date": "2015-05-15",
   "buyer_name": "Vojenský technický ústav, s.p.",
   "supplier": "TATRA DEFENCE SYSTEMS s.r.o.",
   "value_czk": "36000000.00",
   "flags": "R1",
   "example_for": "R1"
  },
  {
   "contract_id": "37307161",
   "url": "https://smlouvy.gov.cz/smlouva/39677289",
   "signed_date": "2026-09-25",
   "buyer_name": "Povodí Moravy, s.p.",
   "supplier": "RiverForge s.r.o.",
   "value_czk": "25555555.00",
   "flags": "R1",
   "example_for": "R1"
  },
  {
   "contract_id": "37052577",
   "url": "https://smlouvy.gov.cz/smlouva/39412013",
   "signed_date": "2026-09-03",
   "buyer_name": "Město Žatec",
   "supplier": "Nemocnice Žatec, z.ú. v likvidaci",
   "value_czk": "45119860.59",
   "flags": "R2",
   "example_for": "R2"
  },
  {
   "contract_id": "36949515",
   "url": "https://smlouvy.gov.cz/smlouva/39305427",
   "signed_date": "2026-08-27",
   "buyer_name": "Střední odborné učiliště včelařské – Včelařské vzdělávací centrum, státní příspěvková organizace",
   "supplier": "Střední odborné učiliště včelařské - Včelařské vzdělávací centrum, o.p.s. v likvidaci",
   "value_czk": "16994259.06",
   "flags": "R2",
   "example_for": "R2"
  },
  {
   "contract_id": "36537326",
   "url": "https://smlouvy.gov.cz/smlouva/38886278",
   "signed_date": "2026-07-22",
   "buyer_name": "Hlavní město Praha",
   "supplier": "Státní statek hl.m. Prahy \"v likvidaci\"",
   "value_czk": "7800000.00",
   "flags": "R2",
   "example_for": "R2"
  },
  {
   "contract_id": "16497839",
   "url": "https://smlouvy.gov.cz/smlouva/38819834",
   "signed_date": "2021-09-14",
   "buyer_name": "Město Horažďovice",
   "supplier": "SeneCura Holding s.r.o. v likvidaci",
   "value_czk": "7574000.00",
   "flags": "R2",
   "example_for": "R2"
  },
  {
   "contract_id": "36624594",
   "url": "https://smlouvy.gov.cz/smlouva/38980398",
   "signed_date": "2026-07-30",
   "buyer_name": "Dostupné bydlení Kamenný vrch II, bytové družstvo",
   "supplier": "Městská část Brno-Nový Lískovec",
   "value_czk": "2099354189.00",
   "flags": "R3",
   "example_for": "R3"
  },
  {
   "contract_id": "36438752",
   "url": "https://smlouvy.gov.cz/smlouva/38773832",
   "signed_date": "2026-07-13",
   "buyer_name": "Ředitelství silnic a dálnic s. p.",
   "supplier": "Metrostav DS a.s.",
   "value_czk": "870481435.74",
   "flags": "R3",
   "example_for": "R3"
  },
  {
   "contract_id": "36470204",
   "url": "https://smlouvy.gov.cz/smlouva/38809504",
   "signed_date": "2026-07-15",
   "buyer_name": "Ředitelství silnic a dálnic s. p.",
   "supplier": "Duna Aszfalt Zártkörüen Müködö Részvénytársaság",
   "value_czk": "817880911.44",
   "flags": "R3",
   "example_for": "R3"
  },
  {
   "contract_id": "36884554",
   "url": "https://smlouvy.gov.cz/smlouva/39238222",
   "signed_date": "2026-08-25",
   "buyer_name": "Povodí Labe, státní podnik",
   "supplier": "Budimex S.A.",
   "value_czk": "587846850.48",
   "flags": "R3",
   "example_for": "R3"
  },
  {
   "contract_id": "36121534",
   "url": "https://smlouvy.gov.cz/smlouva/39538337",
   "signed_date": "2026-06-15",
   "buyer_name": "České vysoké učení technické v Praze",
   "supplier": "Blindspot Solutions s.r.o.",
   "value_czk": "508052228.00",
   "flags": "R4",
   "example_for": "R4"
  },
  {
   "contract_id": "36284652",
   "url": "https://smlouvy.gov.cz/smlouva/38613792",
   "signed_date": "2026-07-01",
   "buyer_name": "Digitální a informační agentura",
   "supplier": "ADASTRA, s.r.o.",
   "value_czk": "310000000.00",
   "flags": "R4",
   "example_for": "R4"
  },
  {
   "contract_id": "36853754",
   "url": "https://smlouvy.gov.cz/smlouva/39206202",
   "signed_date": "2026-08-19",
   "buyer_name": "Město Jindřichův Hradec",
   "supplier": "COMBIN BANSKÁ ŠTIAVNICA, s. r. o.",
   "value_czk": "236509805.75",
   "flags": "R4",
   "example_for": "R4"
  },
  {
   "contract_id": "36853754",
   "url": "https://smlouvy.gov.cz/smlouva/39206202",
   "signed_date": "2026-08-19",
   "buyer_name": "Město Jindřichův Hradec",
   "supplier": "STANTER, a. s.",
   "value_czk": "236509805.75",
   "flags": "R4",
   "example_for": "R4"
  },
  {
   "contract_id": "36326700",
   "url": "https://smlouvy.gov.cz/smlouva/38657252",
   "signed_date": "2026-07-03",
   "buyer_name": "Technologie hlavního města Prahy, a.s.",
   "supplier": "HLAVNÍ MĚSTO PRAHA",
   "value_czk": "5997189.63",
   "flags": "R5",
   "example_for": "R5"
  },
  {
   "contract_id": "36589422",
   "url": "https://smlouvy.gov.cz/smlouva/38930874",
   "signed_date": "2026-07-24",
   "buyer_name": "MČ Praha-Dubeč",
   "supplier": "MV BAU, s.r.o.",
   "value_czk": "5996675.36",
   "flags": "R5",
   "example_for": "R5"
  },
  {
   "contract_id": "36910878",
   "url": "https://smlouvy.gov.cz/smlouva/39265666",
   "signed_date": "2026-08-07",
   "buyer_name": "Správa železnic, státní organizace",
   "supplier": "MS Ruzyňská, s.r.o.",
   "value_czk": "5996280.99",
   "flags": "R5",
   "example_for": "R5"
  },
  {
   "contract_id": "36613974",
   "url": "https://smlouvy.gov.cz/smlouva/38956522",
   "signed_date": "2026-07-30",
   "buyer_name": "Lesy České republiky, s.p.",
   "supplier": "GRACCULUS s.r.o.",
   "value_czk": "5994562.49",
   "flags": "R5 R6",
   "example_for": "R5"
  },
  {
   "contract_id": "36613974",
   "url": "https://smlouvy.gov.cz/smlouva/38956522",
   "signed_date": "2026-07-30",
   "buyer_name": "Lesy České republiky, s.p.",
   "supplier": "GRACCULUS s.r.o.",
   "value_czk": "5994562.49",
   "flags": "R5 R6",
   "example_for": "R6"
  },
  {
   "contract_id": "36955979",
   "url": "https://smlouvy.gov.cz/smlouva/39312043",
   "signed_date": "2026-08-27",
   "buyer_name": "Teplárny Brno, a.s.",
   "supplier": "AVOS VYŠKOV měřící a regulační technika, s.r.o.",
   "value_czk": "5990000.00",
   "flags": "R5 R6",
   "example_for": "R6"
  },
  {
   "contract_id": "37180797",
   "url": "https://smlouvy.gov.cz/smlouva/39545741",
   "signed_date": "2026-09-16",
   "buyer_name": "Národní památkový ústav",
   "supplier": "COMPRIMA s.r.o.",
   "value_czk": "5957567.69",
   "flags": "R5 R6",
   "example_for": "R6"
  },
  {
   "contract_id": "30983512",
   "url": "https://smlouvy.gov.cz/smlouva/39571625",
   "signed_date": "2025-04-22",
   "buyer_name": "Ředitelství silnic a dálnic s. p.",
   "supplier": "MANIFOLD GROUP s.r.o.",
   "value_czk": "5834000.00",
   "flags": "R5 R6",
   "example_for": "R6"
  }
 ]
};
