# NGSAssistant — corpus source manifest

Every card in the corpus must trace to something on this list. If a claim can't be traced here, it doesn't go in. The list is meant to grow; that's the point.

Status legend: **PRIMARY** = the authority we encode from · **SECONDARY** = summary/commentary, usable for orientation but never as the citation of record · **BLOCKED** = paywalled, need another route.

---

## Tier 1 — the rule sets (do outputs ①②④)

| Source | Covers | Status | Route |
|---|---|---|---|
| Döhner et al. **ELN 2022**, *Blood* 140(12):1345 — Diagnosis and management of AML in adults | Output ② prognosis for AML. The risk table. | **PRIMARY** | Verified against clinician-provided local original PDF; PDF not committed. |
| Döhner et al. **ELN 2024**, *Blood* 144(21):2169 — Genetic risk classification for adults receiving **less-intensive** therapies | Output ② for patients not fit for intensive chemo. **Not on the whiteboard. Directly relevant to Case 3 (67F, t-AML).** | To fetch | ashpublications — expect 403, find PMC |
| Khoury et al. **WHO 5th ed 2022**, *Leukemia* 36:1703 | Output ① — AML-defining genetic abnormalities, blast thresholds | Open access ✅ | nature.com/articles/s41375-022-01613-1 · PMC9252913 |
| Arber et al. **ICC 2022**, *Blood* 140(11):1200 | Output ① — the competing classification. Needed because it *disagrees* with WHO. | Open access ✅ | PMC9479031 |
| **ELN-DAVID MRD 2025**, *Blood* 147(11):1147 | Output ④ MRD. **Supersedes the 2021 Heuser consensus** — use 2025. | **BLOCKED** (403) | Find PMC / preprint |
| Bernard et al. **IPSS-M**, *NEJM Evidence* 2022 | Output ② when the answer is MDS — needed for the Case 2 fork | Open access ✅ | evidence.nejm.org/doi/full/10.1056/EVIDoa2200008 |

## Tier 2 — live, keyless, verified working

| Source | Covers | Status |
|---|---|---|
| **CIViC** GraphQL (`civicdb.org/api/graphql`) | Evidence items pre-typed `DIAGNOSTIC` / `PROGNOSTIC` / `PREDICTIVE` = outputs ①②③, each with evidence level A–E and a PubMed citation | ✅ tested, keyless. Query by `featureName`, then `evidenceItems` |
| **ClinicalTrials.gov v2** (`/api/v2/studies`) | Output ③ when there is no licensed therapy — Case 3's honest answer | ✅ tested, keyless |

## Rejected
- **Franklin / Genoox** (on the board). No open API — commercial login. A workshop build would be a scrape or a mock. CIViC does the same job, openly, and arrives pre-typed to the board's own output categories.

---

## What the search changed — corrections to `cases/cases.json`

These are the reason we searched before building. Each one is a claim I wrote from memory that the sources revised.

**1. Case 1 prognosis — right answer, dead reason.**
ELN 2022: *mutated NPM1 without FLT3-ITD* = Favorable; *mutated NPM1 **with** FLT3-ITD* = **Intermediate**. So "intermediate" was right — but ELN 2022 **abolished the allelic ratio** as a criterion (all ratios now intermediate). Case 1's NGS reports "allelic ratio 0.61", which a clinician trained on ELN 2017 will still reach for. **The tool should say the ratio no longer changes the tier.** That is a genuinely useful thing for a second brain to know, and it only surfaced because we checked.

**2. Case 2 is a bigger argument than I drew it.** I framed it as "MDS vs AML". It isn't — it's a *three-way* naming conflict on the same 12%-blast marrow:
- **WHO 5th ed:** NPM1 is AML-defining → **AML**, blast count irrelevant (exceptions: BCR::ABL1, CEBPA)
- **ICC 2022:** requires ≥10% blasts, and 10–19% gets the hybrid category → **"MDS/AML with mutated NPM1"**
- **The clinician wrote:** MDS-EB2

Three systems, three names, one marrow. And the secondary summaries I read **contradict each other** on this exact point — which is the strongest possible argument for a corpus built from primaries and a tool that *shows the fork instead of picking a side*. This case is now the centrepiece of the demo.

**3. Case 3's "no assessment" distractor is broken — BCOR is a corpus hit.**
ELN 2022's adverse MDS-related gene list is: **ASXL1, BCOR, EZH2, RUNX1, SF3B1, SRSF2, STAG2, U2AF1, ZRSR2**. I picked BCOR as the gene that would miss *both* corpus and CIViC. It's on the list. Need a different gene to demonstrate the honest dead-end. (Also note **SRSF2** in Case 2 is on this list too — it isn't inert background, it's an adverse-risk gene, and the tool must say so.)

**4. The MRD source on the board is out of date.** The 2021 ELN MRD consensus has been superseded by the **2025 ELN-DAVID update**. Corpus still uses 2021 until the 2025 primary is added.

**5. TP53 VAF threshold is now resolved from the ELN 2022 primary.** ELN 2022 uses TP53 mutation at a variant allele fraction of at least 10%, irrespective of monoallelic or biallelic TP53 status. This was verified from the clinician-provided local original PDF; the PDF is not committed.

---

## Open, needs a decision
- Remaining ASH-hosted sources may still require PMC versions, institutional access, or the clinician's own PDF library. **Flagged for the clinician — they will have these papers.**
