# Data in Brief – Draft Structure for Livingstone City Council Dataset

**livingstone city council dataset team4:**  
A multi-source dataset of civic leadership, Constituency Development Fund projects and administrative information for Livingstone City Council, Zambia (2022–2026)

**Authors:**  
Samson Mwale - 2022052196  
Nathan Sachitembe - 2022020446  
Taurai Chiponde - 2021425614  
Beauty Mukwilima - 2021487474  
Robert Muchinga - 2021392414  

**Affiliation:** Department of Computer Science, University of Zambia

---

## Abstract
This dataset compiles publicly available information on Livingstone City Council, the local authority governing Zambia’s tourist capital. It contains structured records of civic leaders (Mayor, Town Clerk, Deputy Mayor and Ward Councillors), Constituency Development Fund (CDF) projects with monetary values where disclosed, bursary disbursements, and key administrative attributes. Data were curated from the official council website, official social media statements, and verified secondary sources between 2022 and 2026. The dataset is released in pipe-separated CSV format to support research on decentralisation, local government transparency, CDF effectiveness, and open government data in Zambia.

## Keywords
Livingstone City Council; Constituency Development Fund; Local Government; Zambia; Open Data; Civic Leaders; Decentralisation

## Specifications Table
| Item | Detail |
|------|--------|
| Subject | Social Sciences / Local Government / Data Mining |
| Specific subject area | Local authority administration and public finance in Zambia |
| Type of data | Tables (CSV) |
| How data were acquired | Manual curation and structured extraction from public web sources and official statements |
| Data format | Raw and cleaned CSV (pipe-separated) |
| Parameters for data collection | Publicly available information relating to leadership, CDF projects, bursaries and administrative facts |
| Description of data collection | Compilation from Livingstone City Council website, official Facebook posts, Diggers News, ZNBC and related public records |
| Data source location | Livingstone, Southern Province, Zambia |
| Data accessibility | Repository name: [Your Kaggle dataset name]<br>Direct URL: [to be filled after upload]<br>Instructions for accessing: Publicly available on Kaggle |

## Value of the Data
- Provides the first structured, machine-readable compilation of Livingstone City Council leadership and recent CDF investments.
- Enables comparative analysis across Zambian local authorities.
- Supports transparency research and citizen monitoring of CDF utilisation.
- Useful for teaching data cleaning, web data extraction and open government data concepts.
- Serves as a baseline for longitudinal tracking of local development projects in Livingstone.

## Data Description
Four CSV files are provided:

1. **Civic Leaders** – 22 records covering the Mayor, Town Clerk, Deputy Mayor and 19 Ward Councillors with associated wards.
2. **CDF Projects** – Project-level records including name, ward, year, amount (ZMW), category, status, description and full source attribution.
3. **Bursaries Summary** – Aggregated figures for secondary school and skills development bursaries (2025 disbursed and 2026 budgeted).
4. **Administrative Summary** – Key factual attributes about the Council (contact details, legal framework, IDP reference, etc.).

## Experimental Design, Materials and Methods
Data collection combined direct inspection of the Livingstone City Council website (despite SSL certificate limitations) with systematic review of official social media announcements and reputable news reports. All monetary values were standardised to numeric ZMW. Ward names were normalised. Every record retains explicit source and source URL fields to ensure reproducibility and auditability. No private or non-public data were included.

## Limitations
- Incomplete monetary disclosure for some CDF projects.
- Official website technical issues restricted fully automated scraping.
- Ongoing constituency delimitation may affect future ward boundaries.
- Full approved budgets and detailed LGEF utilisation figures are not comprehensively published.

## Ethics Statement
Only publicly available information was used. No personal data beyond publicly listed official roles were collected.

## Credit Author Statement
Samson and Taurai worked on Sourcin and Cleaned the cdf and finance records. Robert and Beauty Sourced and Cleaned the Bursary and Administrative Summary and Nathan Sachitembe on the Civic Leader. All subsequent duties were divided equally with full participation from the team members.  

## Acknowledgements
We thank the course instructor of CSC 4792 Doc. Lighton Phiri for guidance and the Livingstone City Council for maintaining public information channels.

## References
- Local Government Act No. 2 of 2019 (as amended).
- Livingstone City Council official website and social media.
- Diggers News, ZNBC and related public reports (2024–2026).
- Phiri, L. (2026). A Multi-Source Dataset for CS1 Failure Prediction (exemplar).

---

**Instructions for final submission**
1. Download the official Data in Brief Word template from Elsevier.
2. Copy the content above into the correct sections of the template.
3. Add your full author list, ORCID (if available), and exact Kaggle URL after upload.
4. Export to PDF and submit via Moodle.
