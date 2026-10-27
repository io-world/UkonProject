---
type: raw-source
immutable: true
source: Colorado Secretary of State business entity data (Colorado Information Marketplace, dataset 4ykn-tg5h)
retrieved: 2026-10-26
format: json-in-markdown
---

# Colorado business entity records — "Sage Dentist*" and "Sloan* Dental"

> REAL public records, retrieved 2026-10-26 from the state's open-data copy of the Secretary of
> State business registry. Two searches:
> - [entity name like "%SAGE DENTIST%"](https://data.colorado.gov/resource/4ykn-tg5h.json?$where=upper(entityname)%20like%20%27%25SAGE%20DENTIST%25%27)
> - [entity name like "%SLOAN%DENTAL%"](https://data.colorado.gov/resource/4ykn-tg5h.json?$where=upper(entityname)%20like%20%27%25SLOAN%25DENTAL%25%27)
>
> What it shows: exactly one entity in **Good Standing** at 2750 W 29th Ave (Sage Dentistry, PLLC,
> formed 2015-06-02). A second entity with the practice's own trade name, **Sloans Lake Dental PLLC**,
> sits at the same address with the same agent but has been **Delinquent since May 1, 2022**. Six
> numbered "Sage Dentistry" entities (former offices in Lakewood, Lafayette, Boulder, Arvada and
> Denver) were dissolved between 2016 and 2024. An unrelated "SLOANS LAKE DENTAL PLLC" existed
> 2005–2006 under a different dentist.

Pipeline code reads the JSON block below. Keep it valid JSON.

```json
{
  "retrieved": "2026-10-26",
  "records": [
    {"entity_id": "20151370188", "name": "Sage Dentistry, PLLC", "status": "Good Standing", "formed": "2015-06-02", "type": "DLLC", "principal_address": "2750 W 29th Ave, Denver, CO 80211", "agent": "Sage Elizabeth Pollack, 2750 W 29th Ave, Denver, CO 80211"},
    {"entity_id": "20208083017", "name": "Sloans Lake Dental PLLC", "status": "Delinquent (since 2022-05-01)", "formed": "2020-12-17", "type": "DPC", "principal_address": "2750 W 29th Ave, Denver, CO 80211", "agent": "Sage Pollack, 2750 W 29th Ave, Denver, CO 80211"},
    {"entity_id": "20051017632", "name": "SLOANS LAKE DENTAL PLLC", "status": "Voluntarily Dissolved (2006-06-19)", "formed": "2005-02-01", "type": "DLLC", "principal_address": "1776 S. Jackson St, Suite 612, Denver, CO 80210", "agent": "Peter J. Mirabito DDS"},
    {"entity_id": "20161256592", "name": "Sage Dentistry II, PLLC", "status": "Voluntarily Dissolved (2024-03-04)", "formed": "2016-04-11", "type": "DLLC", "principal_address": "2750 W 29th Ave, Denver, CO 80211", "agent": "Sage Pollack"},
    {"entity_id": "20161667776", "name": "Sage Dentistry III, PLLC", "status": "Voluntarily Dissolved (2022-02-01)", "formed": "2016-09-30", "type": "DLLC", "principal_address": "4150 Darley Ave, #7, Boulder, CO 80305", "agent": "Sage Pollack"},
    {"entity_id": "20161782501", "name": "Sage Dentistry IV, PLLC", "status": "Voluntarily Dissolved (2023-10-25)", "formed": "2016-11-21", "type": "DLLC", "principal_address": "1120 W South Boulder Rd Ste 204, Lafayette, CO 80026", "agent": "Sage Pollack"},
    {"entity_id": "20171166618", "name": "Sage Dentistry V, PLLC", "status": "Voluntarily Dissolved (2024-03-04)", "formed": "2017-02-28", "type": "DLLC", "principal_address": "325 Teller Street, Suite 280, Lakewood, CO 80226", "agent": "Sage Pollack"},
    {"entity_id": "20171658797", "name": "Sage Dentistry VI, PLLC", "status": "Voluntarily Dissolved (2023-10-24)", "formed": "2017-08-29", "type": "DLLC", "principal_address": "8725 Wadsworth Blvd, Suite B, Arvada, CO 80003", "agent": "Sage Pollack"},
    {"entity_id": "20181730664", "name": "Sage Dentistry VII, PLLC", "status": "Voluntarily Dissolved (2022-02-02)", "formed": "2018-09-18", "type": "DLLC", "principal_address": "3737 E. 1st Avenue, Denver, CO 80206", "agent": "Sage Pollack"},
    {"entity_id": "20161248063", "name": "Sage Dentistry 2, PLLC", "status": "Voluntarily Dissolved (2016-08-03)", "formed": "2016-04-06", "type": "DLLC", "principal_address": "16205 W 64th Ave, Unit 200, Arvada, CO 80007", "agent": "Sage Pollack"},
    {"entity_id": "20041240853", "name": "Sage Dentistry of Arvada, PLLC", "status": "Voluntarily Dissolved (2016-08-08)", "formed": "2004-07-12", "type": "DPC", "principal_address": "16205 W 64th Ave, Ste 200, Arvada, CO 80007", "agent": "R. Jeffrey Wilkin"}
  ]
}
```
