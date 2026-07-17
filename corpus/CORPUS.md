# Maintaining the NGSAssistant corpus from PDFs

This file is for coding LLMs and human reviewers extending the corpus from source papers dropped into `corpus/pdfs/`.

The corpus is a curated evidence library, not a summary notebook. Add only claims that the assistant should be allowed to repeat to a clinician, and make every claim traceable to a named source.

## Inputs

- Put source PDFs in `corpus/pdfs/` using a stable, descriptive filename, for example `eln-2022-dohner-blood.pdf`. This is a local staging folder; PDFs are gitignored and should not be redistributed unless you have explicit rights.
- Do not paste patient-identifiable information into the corpus.
- Use PDFs locally to verify cards, then commit the derived corpus/docs changes rather than the PDF. In `encoded_from`, record that verification came from a clinician-provided local PDF.

## Files to edit

- `corpus/cards.json` — source metadata and evidence cards.
- `corpus/SOURCES.md` — source manifest and open/pending/blocked status.
- `README.md` — only if the public description of corpus coverage changes.
- `corpus/HOW_TO_ADD_A_CARD.md` — human-facing card format guide; update only when the schema or workflow changes.

## Workflow for a newly dropped PDF

1. **Extract the text.** Prefer `pdftotext -layout corpus/pdfs/<file>.pdf -` when available. Inspect relevant tables and footnotes, not just keyword hits.
2. **Identify the source.** Add or update one entry in the `sources` block of `corpus/cards.json` with citation, URL/DOI if available, provenance, and local verification note.
3. **Choose provenance honestly.** Use `primary` only when encoding from the original paper/guideline. Use `secondary_pending_verification` only when the card is based on a paper that reproduces or discusses another source.
4. **Keep source boundaries clean.** If a validation cohort comments on a guideline, do not attach that caveat to the guideline source. Add the validation paper as its own source/card if the claim is worth retaining.
5. **Create one card per retrievable clinical rule.** A good card answers one of: `diagnosis`, `prognosis`, `therapy`, or `mrd`.
6. **Use literal, compact claims.** State what the source says in one or two plain sentences. Do not infer beyond the text.
7. **Add firing constraints.** Use `requires_present`, `requires_absent`, `cytogenetic`, `clinical_trigger`, and `implies_disease` so the card fires only in the right clinical context.
8. **Mark caveats deliberately.** Use `caveat` only for qualifications from the same source. Use `note_to_assistant` for presentation guidance, not extra evidence.
9. **Update documentation.** Reflect changed source status in `corpus/SOURCES.md` and, if user-facing coverage changes, `README.md`.
10. **Validate.** Run JSON validation and corpus retrieval smoke tests before finishing.

## Validation commands

```bash
python -m json.tool corpus/cards.json >/dev/null
python scripts/retrieve.py --genes TP53,NPM1,FLT3,SRSF2 --disease AML --no-network
python scripts/retrieve.py --case cases/case1-fit.json --no-network
python scripts/retrieve.py --case cases/case3-dead-end.json --no-network
```

Also search for stale status text after upgrading a source:

```bash
grep -R "second-hand\|secondary_pending_verification\|BLOCKED\|unresolved" README.md corpus/SOURCES.md corpus/cards.json
```

## Non-negotiable rule

Do not write a claim the source does not make. A plausible but unsourced card damages the whole tool because the assistant is designed to be trusted only when every line can be traced back to evidence.
