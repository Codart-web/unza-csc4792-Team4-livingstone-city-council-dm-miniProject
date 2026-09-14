# CDF Findings

## Scope

The CDF review found four sources suitable for extracting structured observations for the Livingstone City Council project:

- `SRC-CDF-012` - Approved 2024 CDF Community Projects
- `SRC-CDF-013` - Approved Skills Development Bursaries 2025
- `SRC-CDF-022` - Approved CDF 2025 Loans, Livingstone Constituency
- `SRC-CDF-034` - CDF Project Progress Tracker

The remaining acquired CDF files are mainly application forms, legislation, guidelines, adverts, blank templates, or general explanatory material. They are useful as contextual or schema-reference evidence, but they do not provide approved Livingstone records for the final CDF observation tables.

## Source observations

### SRC-CDF-012 - Approved 2024 CDF Community Projects

The two-page council document contains 22 approved community-project records. The visible fields are:

- serial number;
- project name, description, and location;
- ward; and
- project type.

Examples include roads, drainage, health, water reticulation, construction, solar-powered boreholes, solar streetlights, and supply-and-delivery projects. The document does not visibly provide project cost, contractor, completion percentage, or implementation status for these records. Those fields must remain missing unless supported by another source.

### SRC-CDF-013 - Approved Skills Development Bursaries 2025

This source belongs to the CDF skills-development bursary stream and should be reviewed as an approved-beneficiary source. Extract only the records and fields that are actually present in the approved list. Do not copy fields from the blank skills-bursary application form into the dataset. Do not publish NRC numbers, phone numbers, addresses, or other personal identifiers if they appear in the source; retain only the minimum non-identifying fields needed for the assignment and document any exclusions.

### SRC-CDF-022 - Approved CDF 2025 Loans

The three-page council document contains 59 approved loan records. The visible fields are:

- serial number;
- name of business;
- type of business;
- amount applied for in ZMW; and
- ward.

The document reports a total of `5,488,578.00` ZMW. This total should be checked against the sum of the extracted loan amounts during validation. The source does not visibly provide loan status, repayment status, contractor, completion percentage, or project-cost fields.

### SRC-CDF-034 - CDF Project Progress Tracker

The tracker page provides project-progress observations by year and category. The captured tracker view shows ward, project description, category filters, and completion percentage. In the captured view, the following 2024 observations are visible:

- Mulungushi Ward - Construction of an ablution block at Malota Community School - 100%.
- Simonga Ward - Construction of staff house at Katubya Primary School - 100%.

The tracker should be treated as a progress/status source. Its records must be checked against the selected year and category before extraction. A tracker percentage is not the same thing as a project cost or financial allocation.

## Recommended CDF tables

Keep observations separate by meaning:

1. `cdf_projects`: one row per approved community project, initially from SRC-CDF-012 and the tracker where project references can be reconciled.
2. `cdf_loans`: one row per approved loan business from SRC-CDF-022.
3. `cdf_skills_bursaries`: one row per approved bursary record from SRC-CDF-013, using only non-identifying fields supported by the source.

Do not merge loans, bursaries, and community projects into one table merely because all are funded under CDF.

## Source handling decision

Do not delete the non-useful sources. Preserve them in `data/raw/` and keep their register rows because they document the acquisition process and provide legal, procedural, or schema context. Mark them as reviewed and not used for final observations, or retain their existing acquisition status with a note explaining why they were excluded. Only the four sources above should be promoted to verified extraction sources after the files are manually checked against their titles and contents.

No values should be taken from the leader's unverified news-post notes unless the original URLs are opened and the facts are independently confirmed.
