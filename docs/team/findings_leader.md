# Findings — Leader's own slice ("other" domain: site navigation + unlabeled news posts)

## Site-navigation pages (18 rows, rejected)
- About Us, Contact Us, FAQs, Mandate, Departments, Civic Leaders,
  Complaints, Investment Opportunities, Services, Application Forms,
  Publications, category-index nav pages (About The Council, Core
  Values, Mission statement, Vision), 3 irrelevant news posts.
- No structured/tabular content. Confirmed by title/context alone,
  no PDF extraction relevant here (these are HTML site-navigation
  pages, not documents).

## 3 kept contextual news posts (verified, acquired as HTML evidence)
- Narrative-only: Kashitu Local Area Plan (x2), Cash for Work
  sensitisation. No cost/ward/status fields present in the text.
  Confirmed suitable for paper background/context citation only, not
  row-level extraction.

## 3 reclassified CDF project records (moved to Member 2's domain)
- These DID contain structured facts (ward, cost, funding year,
  completion %, one contractor name) extracted directly from news
  article text during manual review. See
  docs/source_register/for_member_2.csv rows SRC-CDF-038 to 040 for
  the extracted values themselves.

## Overall assessment
The LEADER-owned "other" domain does not itself produce a dataset.
Its only genuine contribution to the final Kaggle datasets is the 3
CDF-relevant records already reclassified into the CDF domain. This
is expected and consistent with how this domain was scoped from the
start (site furniture + miscellaneous, not a planned data source).
