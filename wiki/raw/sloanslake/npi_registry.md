---
type: raw-source
immutable: true
source: CMS NPPES NPI Registry API
retrieved: 2026-10-26
format: json-in-markdown
---

# NPI registry — the practice, its owner, and look-alikes

> REAL public records from the federal National Plan and Provider Enumeration System (NPPES),
> retrieved 2026-10-26:
> - [Dental organizations in ZIP 80211](https://npiregistry.cms.hhs.gov/api/?version=2.1&enumeration_type=NPI-2&postal_code=80211&taxonomy_description=dent*&limit=100)
> - [Sage Pollack (individual)](https://npiregistry.cms.hhs.gov/api/?version=2.1&first_name=sage&last_name=pollack&limit=10)
> - [Organizations named "Sloan*" in Colorado](https://npiregistry.cms.hhs.gov/api/?version=2.1&organization_name=sloan*&state=CO&limit=50)
> - [Organizations named "Sage Dent*"](https://npiregistry.cms.hhs.gov/api/?version=2.1&organization_name=sage%20dent*&limit=50)
>
> The practice's organization record is enumerated the same day the LLC was formed (2015-06-02),
> which ties the trade name to the legal entity. Its listed phone (720-231-2755) differs from the
> website's (303-477-7776); the individual record for Dr. Pollack carries the website number.

```json
{
  "retrieved": "2026-10-26",
  "practice": {
    "npi": "1316327604", "entity_type": "organization",
    "name_as_registered": "SAGE DENTISTRY PLLC SLOANS LAKE DENTAL",
    "enumerated": "2015-06-02", "last_updated": "2015-06-02",
    "practice_address": "2750 W 29th Ave, Denver, CO 80211", "phone": "720-231-2755",
    "authorized_official": "Sage Elizabeth Pollack, DMD (Owner)"
  },
  "owner": {
    "npi": "1992925531", "name": "Sage E. Pollack, D.M.D.", "enumerated": "2007-04-26",
    "practice_address": "2750 W 29th Ave, Denver, CO 80211-3053", "phone": "303-477-7776",
    "taxonomy": "122300000X Dentist", "license": "CO 00202525"
  },
  "lookalikes": [
    {"npi": "1245524800", "name": "DARREN BENNETT DDS PC", "dba": "SLOANSIDE DENTAL", "address": "2045 Sheridan Blvd, Suite H, Edgewater, CO 80214", "phone": "303-274-1100", "official": "Darren Alexander Bennett, DDS (Owner)"},
    {"npi": "1174158992", "name": "DENVER HEALTH AND HOSPITAL AUTHORITY", "dba": "SLOAN'S LAKE PRIMARY CARE", "address": "4007 W Colfax Ave, Denver, CO 80204", "note": "medical clinic, not dental"},
    {"npi": "1790339463", "name": "MY LOCAL COLORADO DENTAL PRACTICE, LLC", "dba": "Sage Dental Care", "address": "2695 Northpark Dr Ste 104, Lafayette, CO 80026", "note": "unrelated multi-location Colorado dental group with a 'Sage' brand"},
    {"npi": "1295276061", "name": "SAGE DENTAL GROUP OF GEORGIA, LLC", "dba": null, "address": "876 Buford Rd, Cumming, GA 30041", "note": "large FL/GA dental chain, unrelated"}
  ]
}
```
