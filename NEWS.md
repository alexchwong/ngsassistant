# NEWS

## v0.1.1

- Refined NGS report generation so the assistant produces a verifier-friendly working draft before converting it into a concise clinical report.
- Added final report rules for diagnosis, prognosis, targeted therapy, MRD, and optional clonal-marker paragraphs.
- Tightened citation requirements, especially for WHO 5th edition and ICC 2022 diagnostic terminology.
- Added fallback guidance for blocked CIViC or ClinicalTrials.gov retrieval, including `403` errors, so network failure is not treated as negative evidence.
- Moved generated per-case working files out of the repository root and into temporary working directories.
- Verified the ELN 2022 AML corpus cards against the primary Blood paper and updated the source status from provisional to primary.
- Resolved the ELN 2022 TP53 adverse-risk threshold as VAF at least 10%.
- Added a corpus-maintenance workflow for deriving evidence cards from local PDFs without committing the PDFs.
- Added WHO 5th edition corpus support for MDS with low blasts and SF3B1 mutation.
- Added a new MDS/SF3B1/DNMT3A example case for pipeline testing.

## v0.1.0

- Seed NGSAssistant skill, evidence corpus, retrieval script, verification script, documentation, and initial synthetic cases.