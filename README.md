# NGSAssistant

**A second brain for the moment the gene list lands on top of the marrow.**

You have a bone marrow diagnosis in front of you. An NGS panel has just come back. Now you have to work out whether the mutations agree with the diagnosis, what they do to the risk group, whether any of them open a treatment, and whether any of them can be followed as MRD — which means holding ELN, WHO, ICC, IPSS-M and a variant database in your head at the same time.

That's the moment this is for. You give it the case; it gives you four answers, and it shows you where every single one came from.

**You decide. It assists.** It will argue with you. It will not overrule you.

---

## The four answers

Straight off the whiteboard:

1. **Is the NGS consistent with the diagnosis?**
2. **Prognosis** — better, worse, or no change
3. **Therapy** — is anything targetable
4. **MRD biomarker** — can any of these be followed

Plus a fifth section you should read every time: **Not assessed** — the genes it had nothing to say about. More on why that matters below.

---

## The one thing to understand before you use it

**This tool has no haematology knowledge. It has a library.**

That sounds like a weakness. It's the entire point.

If you ask a chatbot about NPM1, it will tell you something fluent, confident, and *unsourced* — and roughly right, most of the time. The times it's wrong look exactly like the times it's right. On a gene's prognostic weight, that's not a tool you can use, because you'd have to check every line anyway.

So this one is built the other way round. It is **only allowed to say things it can point at a source for.** Behind the scenes it runs a search across a curated library of guideline cards, then a live open variant database (CIViC), then the trials registry. Anything it finds, it can say — with the citation. Anything it doesn't find, it **cannot** say, and instead it tells you it doesn't know.

Then a second check runs over its answer and rejects any citation that doesn't match something it actually retrieved. If it invents a reference, the answer doesn't reach you.

**Practical consequence:** this tool will say *"I don't know"* far more often than a chatbot will. That's not it being unhelpful. That's the only reason you can trust the times it *does* answer.

### Why "Not assessed" is the most important section

Every answer ends with a list of the genes it couldn't assess, **by name**.

This matters more than it looks. A gene that quietly vanishes from a report is indistinguishable — to you, reading it — from a gene that was checked and found unimportant. Those are completely different things, and only one of them is true. So it never drops one silently.

It's also your to-do list. Every gene on it is a precise, specific job for growing the library (see *Making it better*, below).

---

## Getting it working (Claude desktop app — no coding)

You need a **Claude Pro, Max, Team or Enterprise** account.

**1. Download the skill.**
Go to the repository page and download **`ngsassistant.zip`** — it's in the file list. (Or: the green **Code** button → **Download ZIP**, then look inside for `ngsassistant.zip`.) Don't unzip it.

**2. Turn Skills on.**
In the Claude app: **Settings → Capabilities** (on some versions, **Features**). Make sure **Code execution** is enabled — the skill needs it to run its searches.

**3. Upload it.**
Same screen → **Skills** → **Upload skill** → choose `ngsassistant.zip`.

**4. Check it's alive.** Start a new chat and type:

> Use NGSAssistant and run case 2.

If it comes back with a four-part answer about a 71-year-old man whose marrow says MDS but whose gene list says something else — you're up and running.

> **If it doesn't trigger:** just say *"use the NGSAssistant skill"* explicitly. Skills sometimes need to be called by name the first time.

---

## Using it on a case

Paste a case in. Free text is fine — you don't need a form — but it works best when it has all of this:

```
Age/sex:            58F
Clinical problem:   6 weeks fatigue, bruising, bleeding gums. No prior chemo or RT.
Blood count:        WCC 42.1, Hb 82, Plt 35, Neut 1.1
Film:               45% blasts, occasional Auer rods, cup-shaped nuclei
Marrow diagnosis:   AML, 62% blasts. Karyotype 46,XX — normal.
NGS:                NPM1  c.860_863dup p.(Trp288fs)   VAF 41%
                    FLT3  ITD, 42bp, allelic ratio 0.61  VAF 33%
                    DNMT3A c.2645G>A p.(Arg882His)   VAF 46%
```

**Include the VAF.** It's what separates a driver clone from CHIP-level background, and it changes the answer. If you leave it out, the tool will ask.

### Then argue with it

This is the bit a static report can't do. Push back. It has the evidence in front of it and it will show you its working:

- *"But the blasts were only 12% — does that change it?"*
- *"Show me exactly which paper says that."*
- *"What if the marrow is wrong and this is really AML?"*
- *"Why can't I use DNMT3A as an MRD marker? It's sitting at 46%."*

If a question takes it outside its library, it will go and search again rather than guess. If it still has nothing, it will say so.

---

## The three worked cases

Try these before you trust it with anything of your own. Each one is built to show you a different thing — including the ways the tool can be *unhelpful*, which you need to see.

**`run case 1`** — AML: NPM1 + FLT3-ITD + DNMT3A.
Everything fires. It also catches two traps: the FLT3-ITD **allelic ratio no longer changes the risk tier** under ELN 2022 (if you trained on ELN 2017 you'll still reach for it), and **DNMT3A at 46% VAF looks like a beautiful MRD marker and is not one.**

**`run case 2`** — marrow says MDS-EB2 (12% blasts); NGS shows NPM1 at 38%.
**The interesting one.** The gene list argues with the marrow. WHO 5th edition calls this AML. ICC 2022 calls it *MDS/AML*. The reporting haematologist called it MDS-EB2. Three systems, three names, one marrow. The tool lays out all three and **refuses to pick** — because the choice of classification is yours, and a confident single answer here would be a lie.

**`run case 3`** — therapy-related AML: TP53 + complex karyotype.
**The one that earns trust.** Adverse risk, **no targeted therapy, no valid MRD marker.** It says "there is nothing here" instead of manufacturing something. It offers recruiting trials instead. And `SMC3` comes back as *not assessed* — visible, not vanished.

A second brain that always has good news isn't a second brain. It's a liability that agrees with you.

---

## What's in the library right now (and what isn't)

Be aware of these before you lean on it.

| | |
|---|---|
| **ELN 2022** — AML risk | ✅ From the original Blood paper. Includes the 2022 AML genetic risk table and the TP53 VAF threshold. |
| **WHO 5th edition (2022)** | ✅ From the original |
| **ICC 2022** | ✅ From the original. Included *because* it disagrees with WHO — that disagreement is clinically real and you should see it |
| **ELN MRD consensus** | ✅ From the original — but the **2021** version. The 2025 update is paywalled and isn't in yet |
| **IPSS-M** — MDS risk | ✅ Named, but **never calculated.** The tool doesn't collect the inputs an IPSS-M score needs, so it will point you at the calculator rather than pretend |
| **CIViC** | ✅ Live. Open somatic variant database, PubMed-cited |
| **ClinicalTrials.gov** | ✅ Live. Recruiting trials |

**Not in there at all:** ELN 2024 (risk for patients on *less-intensive* therapy — directly relevant to your older and unfit patients), MPN, anything lymphoid. Scope is AML and MDS.

**Still to add:** ELN 2024 for patients receiving less-intensive therapy, the 2025 ELN-DAVID MRD update, MPN, and anything lymphoid.

---

## Making it better — this is the part meant for you

The library is a **seed**. It was built in an afternoon to prove the idea. It is meant to be grown by the people using it, and growing it does **not** require writing code.

**The easiest way: just ask Claude to do it.**

Open a chat with the skill loaded and say something like:

> I'm adding to the NGSAssistant corpus. Here's the ELN 2024 paper [attach the PDF]. Add cards for the less-intensive-therapy risk criteria, cite it properly, and mark the source as primary.

Claude will write the new cards into `corpus/cards.json` for you and hand the file back. You re-upload the skill, and it now knows about ELN 2024. That's the whole loop.

**Good first jobs, in order:**

1. **Give it the 2025 ELN MRD update.** The MRD answers are currently one guideline generation behind.
2. **Add ELN 2024** (less-intensive therapy).
3. **Work the "Not assessed" lists.** Every gene that shows up there is a gap someone has now noticed. That's the flywheel.

If you'd rather edit the file directly, [`corpus/HOW_TO_ADD_A_CARD.md`](corpus/HOW_TO_ADD_A_CARD.md) explains the format. If you're dropping PDFs into the repository and asking a coding LLM to process them, use [`corpus/CORPUS.md`](corpus/CORPUS.md) as the workflow checklist. It's plain JSON — a citation, and a sentence saying what the source says.

**The one rule when adding anything:** don't write a claim the source doesn't actually make. The whole value of this tool is that you can point at any line and be shown where it came from. One card containing a plausible-sounding fact that no paper says, and that guarantee is gone — and nobody will be able to tell which line it was.

---

## Limits — please read

This is a **prototype**, built in a design-thinking workshop. It is a decision *aid*, not a decision.

- **Not a medical device. Not validated. Not for use on real patients.**
- The three cases are **synthetic**. No patient data. **Do not paste identifiable patient information into it.**
- It does not prescribe. It shows you what the evidence says exists.
- It does not compute IPSS-M, and won't pretend to.
- When it says *"no assessment"*, that means **the library is incomplete** — not that the finding is unimportant.

It is designed so that its ignorance is visible. That's the feature.

---

## For developers

Python 3.9+, standard library only. No API keys — CIViC and ClinicalTrials.gov are open and keyless.

```bash
python scripts/retrieve.py --case cases/case2-tension.json > bundle.json   # corpus -> CIViC -> trials -> stop
python scripts/verify.py --bundle bundle.json --draft draft.md            # every citation must trace to retrieved evidence
python scripts/retrieve.py --genes TP53,SETBP1 --disease AML              # quick lookup
python scripts/retrieve.py --case cases/case1-fit.json --no-network       # corpus only, offline
```

`retrieve.py` decides what evidence the model may see; `verify.py` checks what it did with it. The guarantee lives in the scripts, not in the prompt — a prompt is a request, code is a guarantee. See `SKILL.md` for the reasoning and `corpus/SOURCES.md` for the source manifest.
