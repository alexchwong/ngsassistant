# Growing the corpus

This is the part of NGSAssistant designed to be edited by a haematologist, not a programmer. Adding knowledge is a **data change**, not a code change. You edit one file — `cards.json` — and the tool picks it up on the next run.

Every answer the assistant gives ends with a **Not assessed** section. That's your to-do list. Each entry is a gene it was asked about and had nothing to say on.

## The two-step

### 1. Add the source (once per paper)

In the `sources` block:

```json
"eln24": {
  "citation": "Döhner H, et al. Genetic risk classification for adults with AML receiving less-intensive therapies: the 2024 ELN recommendations. Blood. 2024;144(21):2169.",
  "url": "https://ashpublications.org/blood/article/144/21/2169",
  "provenance": "primary"
}
```

`provenance` is either:

- **`primary`** — you encoded it from the actual paper. Citable as-is.
- **`secondary_pending_verification`** — you encoded it from something that *quotes* the paper (a review, a validation cohort) because the original was paywalled. **The assistant will display this stamp next to any claim built on it.** That's deliberate: a clinician is entitled to know which claims in front of them are second-hand.

Be honest about which one it is. The stamp is not an embarrassment — an un-stamped guess is.

### 2. Add the card

```json
{
  "id": "eln24-tp53-less-intensive",
  "output": "prognosis",
  "disease": ["AML"],
  "genes": ["TP53"],
  "claim": "State the rule in one or two plain sentences, as the source states it.",
  "source": "eln24"
}
```

**`output`** — which of the four questions this answers: `diagnosis`, `prognosis`, `therapy`, `mrd`.

**`genes`** — the gene symbols that make this card relevant. Leave it `[]` for a rule that isn't about a specific gene (how complex karyotype scores, what counts as MRD negativity).

**`claim`** — what the source says. Write it as the source says it. This text goes to the assistant as the *only* thing it is allowed to say on the point, so if it's vague, the answer will be vague.

## Making a card fire only when it should

The retriever is deliberately literal, because a card that fires on the wrong patient is worse than a card that doesn't exist — it arrives with a citation attached and looks true.

| Field | Use it for |
|---|---|
| `requires_present: ["NPM1","FLT3"]` | Card only fires if **all** of these are mutated. This is how "NPM1 **with** FLT3-ITD is intermediate" avoids firing on an NPM1-only panel. |
| `requires_absent: ["FLT3-ITD"]` | Card only fires if these are **not** mutated. This is how "NPM1 **without** FLT3-ITD is favourable" stays out of the way. |
| `cytogenetic: true` | Card only fires if the marrow report actually mentions cytogenetics (complex, monosomy, a translocation). |
| `clinical_trigger: ["prior cytotoxic therapy"]` | Card fires on the clinical text. Negation is handled — *"no prior chemotherapy"* will **not** trigger it. |
| `implies_disease: ["AML"]` | **The important one.** Use it when a lesion defines a different disease from the one the clinician wrote. It makes the tool load *both* rule sets so it can show the clinician the argument rather than silently siding with the marrow report. This is what makes the NPM1-in-an-MDS-marrow case work. |

Two optional fields let you talk directly to the assistant:

- **`caveat`** — a qualification it should voice alongside the claim ("a *single* MDS-related mutation behaved more like intermediate risk in the validation cohort").
- **`note_to_assistant`** — guidance on *how* to use the card. This is where you put clinical judgement about presentation: *"say this whenever a DTA gene is on the panel — the clinician is looking at a mutation at 46% VAF that looks like a perfect MRD marker and isn't one."*

## Check your work

```bash
python scripts/retrieve.py --genes TP53,SETBP1 --disease AML
python scripts/retrieve.py --case cases/case3-dead-end.json
```

Look at which cards fired and what they matched on. Then run the three demo cases and make sure you haven't made a card fire on a patient it shouldn't touch — the fastest way to break this tool is a card that's *almost* right.

## The one thing not to do

Don't write a claim the source doesn't make. The entire value of this tool is that a clinician can point at any line on the screen and be shown where it came from. One card containing a plausible-sounding fact that no paper actually says, and that guarantee is gone — and nobody can tell which line it was.
