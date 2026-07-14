#!/usr/bin/env python3
"""
Evidence retrieval for NGSAssistant. Corpus -> CIViC -> ClinicalTrials.gov -> stop.

This script exists so that "no model recall on medical claims" is a GUARANTEE rather
than a request. A prompt is a request; code is a guarantee. Everything the assistant
is allowed to say about a gene comes back from here, and anything that does not come
back from here has to be reported as "no assessment" rather than filled in from memory.

The chain is deliberate:

  1. CORPUS   - hand-curated cards from named sources (ELN, WHO, ICC, IPSS-M). These
                carry the rule-set logic: risk tiers, defining lesions, MRD validity.
  2. CIViC    - open, keyless, curated somatic evidence. Its evidence items arrive
                already typed DIAGNOSTIC / PROGNOSTIC / PREDICTIVE, which map onto the
                assistant's outputs 1 / 2 / 3, each with an evidence level and a PubMed
                citation. This catches genes the corpus has not reached yet.
  3. TRIALS   - ClinicalTrials.gov v2. Reached for when there is no licensed therapy,
                which is the honest answer more often than anyone would like.
  4. STOP     - a gene that none of the above covers is returned in `unassessed`. It is
                NOT dropped. A silently missing gene is indistinguishable from a gene
                that was considered and cleared, and those are very different things.

Usage:
    python retrieve.py --case path/to/case.json          # a full case
    python retrieve.py --genes NPM1,FLT3,DNMT3A          # a quick gene lookup
    python retrieve.py --case case.json --no-network     # corpus only (offline demo)

Output: an evidence bundle as JSON on stdout. Nothing else. Feed it to the assistant.
"""

import argparse
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

CORPUS = Path(__file__).resolve().parent.parent / "corpus" / "cards.json"

CIVIC = "https://civicdb.org/api/graphql"
TRIALS = "https://clinicaltrials.gov/api/v2/studies"
TIMEOUT = 20

# CIViC evidence types map onto the four whiteboard outputs. Note there is no CIViC
# evidence type for MRD -- MRD validity is a rule-set question, not a variant-annotation
# question, so it can only ever come from the corpus. If the corpus has no MRD card for
# a gene, the honest answer is that we do not know, not that CIViC was quiet.
CIVIC_TO_OUTPUT = {
    "DIAGNOSTIC": "diagnosis",
    "PROGNOSTIC": "prognosis",
    "PREDICTIVE": "therapy",
    "ONCOGENIC": "diagnosis",
    "FUNCTIONAL": "diagnosis",
}

EVIDENCE_QUERY = """
query($feature: String!) {
  evidenceItems(first: 20) {
    nodes {
      id evidenceType evidenceLevel evidenceDirection significance description
      molecularProfile { name }
      disease { name }
      therapies { name }
      source { citationId sourceType title }
    }
  }
  browseVariants(featureName: $feature, first: 10) {
    nodes { id name }
  }
}
"""

# Fetching every evidence item and filtering client-side would be wasteful, so query by
# molecular profile name instead -- CIViC indexes evidence against the profile, and the
# profile name contains the gene symbol.
BY_PROFILE = """
query($name: String!) {
  evidenceItems(molecularProfileName: $name, first: 25) {
    nodes {
      id evidenceType evidenceLevel evidenceDirection significance description
      molecularProfile { name }
      disease { name }
      therapies { name }
      source { citationId sourceType title }
    }
  }
}
"""


def post_json(url, payload):
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json", "Accept": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
        return json.loads(r.read())


def get_json(url):
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
        return json.loads(r.read())


def load_corpus():
    return json.loads(CORPUS.read_text(encoding="utf-8"))


# A trigger phrase preceded by a negation is not a trigger. "No prior chemotherapy" is
# the exact OPPOSITE of "prior chemotherapy", and a naive substring match reads them as
# the same thing -- handing the assistant a card that contradicts the case. Clinical
# notes are dense with negation ("no fever", "denies", "without"), so this is the normal
# case, not an edge case.
NEGATORS = ("no ", "not ", "denies ", "without ", "negative for ", "nil ")


def mentioned(text, phrase):
    """True if `phrase` appears in `text` and is not negated just before it."""
    start = 0
    while True:
        i = text.find(phrase, start)
        if i == -1:
            return False
        window = text[max(0, i - 24):i]
        if not any(neg in window for neg in NEGATORS):
            return True
        start = i + 1


# Cytogenetic cards must see cytogenetics. Firing an adverse complex-karyotype card at a
# patient with a normal karyotype is not a harmless extra -- it is a wrong claim placed
# in front of a clinician with a citation attached to it.
CYTO_MARKERS = (
    "complex", "monosom", "del(5q)", "del(7q)", "del(17p)", "-5", "-7", "-17",
    "inv(3)", "inv(16)", "t(8;21)", "t(16;16)", "t(6;9)", "t(9;22)", "t(3;3)",
    "t(9;11)", "t(8;16)", "abnormalities",
)


def corpus_hits(corpus, genes, disease, clinical_text):
    """Cards whose gene list intersects the panel, plus disease-level and clinical cards.

    Cards with an empty `genes` list are not junk -- they are disease-level rules (how
    complex karyotype scores, what MRD response means, that prior chemotherapy changes
    the classification). They fire on disease or on a clinical trigger, not on a gene.
    """
    genes_upper = {g.upper() for g in genes}
    text = (clinical_text or "").lower()
    hits = []

    for card in corpus["cards"]:
        if card.get("disease") and disease and disease.upper() not in [d.upper() for d in card["disease"]]:
            continue

        card_genes = {g.upper() for g in card.get("genes", [])}
        matched_on = None

        if card_genes & genes_upper:
            matched_on = sorted(card_genes & genes_upper)
        elif not card_genes:
            triggers = card.get("clinical_trigger")
            if triggers:
                if any(mentioned(text, t.lower()) for t in triggers):
                    matched_on = "clinical context"
                else:
                    continue
            elif card.get("cytogenetic"):
                if any(m in text for m in CYTO_MARKERS):
                    matched_on = "cytogenetics"
                else:
                    continue
            else:
                matched_on = "disease-level rule"
        else:
            continue

        # Risk-tier cards are CONDITIONAL, and the conditions are the whole point. "NPM1
        # without FLT3-ITD" is favourable; "NPM1 with FLT3-ITD" is intermediate. Matching
        # on NPM1 alone fires both, and hands the assistant two contradictory tiers to
        # referee -- which is precisely the clinical judgement we are keeping out of the
        # model. So a card can require genes to be present, or require them to be absent,
        # and it only fires when the panel actually satisfies it.
        absent = card.get("requires_absent", [])
        if any(t.split("-")[0].upper() in genes_upper for t in absent):
            continue

        present = card.get("requires_present", [])
        if present and not all(t.split("-")[0].upper() in genes_upper for t in present):
            continue

        src = corpus["sources"][card["source"]]
        hits.append(
            {
                "id": card["id"],
                "output": card["output"],
                "claim": card["claim"],
                "matched_on": matched_on,
                "caveat": card.get("caveat"),
                "gap": card.get("gap"),
                "note_to_assistant": card.get("note_to_assistant"),
                "source": {
                    "id": card["source"],
                    "citation": src["citation"],
                    "url": src["url"],
                    "provenance": src["provenance"],
                    "todo": src.get("todo"),
                },
            }
        )
    return hits


def civic_for_gene(gene, disease_filter=None):
    """CIViC evidence for one gene. Returns [] on any failure -- a flaky network must
    degrade the answer, never fabricate one."""
    try:
        data = post_json(CIVIC, {"query": BY_PROFILE, "variables": {"name": gene}})
        nodes = data.get("data", {}).get("evidenceItems", {}).get("nodes", [])
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, json.JSONDecodeError) as e:
        print(f"[warn] CIViC lookup failed for {gene}: {e}", file=sys.stderr)
        return []

    out = []
    for n in nodes:
        profile = (n.get("molecularProfile") or {}).get("name", "")
        if gene.upper() not in profile.upper():
            continue
        disease = (n.get("disease") or {}).get("name")
        src = n.get("source") or {}
        out.append(
            {
                "id": f"CIViC:EID{n['id']}",
                "output": CIVIC_TO_OUTPUT.get(n.get("evidenceType"), "other"),
                "evidence_type": n.get("evidenceType"),
                "evidence_level": n.get("evidenceLevel"),
                "direction": n.get("evidenceDirection"),
                "significance": n.get("significance"),
                "claim": n.get("description"),
                "molecular_profile": profile,
                "disease": disease,
                "therapies": [t["name"] for t in (n.get("therapies") or [])],
                "source": {
                    "id": f"PMID:{src.get('citationId')}" if src.get("sourceType") == "PUBMED" else src.get("citationId"),
                    "citation": src.get("title"),
                    "url": f"https://pubmed.ncbi.nlm.nih.gov/{src.get('citationId')}/"
                    if src.get("sourceType") == "PUBMED"
                    else None,
                    "provenance": "live_civic",
                },
            }
        )
    return out


def trials_for(condition, gene_terms, max_studies=8):
    """Recruiting trials. This is the honest output when there is no licensed therapy."""
    from urllib.parse import urlencode

    q = urlencode(
        {
            "query.cond": condition,
            "query.term": " OR ".join(gene_terms) if gene_terms else "",
            "filter.overallStatus": "RECRUITING",
            "pageSize": max_studies,
            "fields": "NCTId,BriefTitle,OverallStatus,Phase,LocationCountry",
        }
    )
    try:
        data = get_json(f"{TRIALS}?{q}")
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, json.JSONDecodeError) as e:
        print(f"[warn] ClinicalTrials.gov lookup failed: {e}", file=sys.stderr)
        return []

    out = []
    for s in data.get("studies", []):
        p = s.get("protocolSection", {})
        ident = p.get("identificationModule", {})
        status = p.get("statusModule", {})
        design = p.get("designModule", {})
        nct = ident.get("nctId")
        out.append(
            {
                "id": f"NCT:{nct}",
                "output": "therapy",
                "title": ident.get("briefTitle"),
                "status": status.get("overallStatus"),
                "phase": ", ".join(design.get("phases", []) or []),
                "source": {
                    "id": nct,
                    "citation": f"ClinicalTrials.gov {nct}",
                    "url": f"https://clinicaltrials.gov/study/{nct}",
                    "provenance": "live_clinicaltrials",
                },
            }
        )
    return out


def retrieve(case, network=True):
    corpus = load_corpus()
    ngs = case.get("ngs", [])
    genes = [v["gene"] for v in ngs]
    disease = case.get("disease") or infer_disease(case.get("marrow_diagnosis", ""))
    clinical = " ".join(
        str(case.get(k, "")) for k in ("clinical_problem", "marrow_diagnosis", "film")
    )

    cards = corpus_hits(corpus, genes, disease, clinical)

    # THE FORK.
    #
    # Retrieval keyed only on the diagnosis the clinician wrote has a blind spot that
    # happens to sit exactly where this tool is most useful: if the marrow says MDS and
    # an NPM1 mutation says AML, loading only the MDS rule set means the assistant is
    # structurally incapable of showing the argument. It would have no ELN cards to argue
    # with -- and it would not know that it didn't.
    #
    # So when a diagnosis card fires that implies a DIFFERENT disease from the one
    # written, we load that disease's rule set too, and label every card with the disease
    # it belongs to. The assistant then has both branches in hand and can lay them side
    # by side, which is the whole job.
    implied = {
        d
        for card in corpus["cards"]
        for d in card.get("implies_disease", [])
        if card["id"] in {c["id"] for c in cards} and d.upper() != (disease or "").upper()
    }

    for d in cards:
        d["for_disease"] = disease

    forked = []
    for other in sorted(implied):
        for c in corpus_hits(corpus, genes, other, clinical):
            if c["id"] not in {x["id"] for x in cards}:
                c["for_disease"] = other
                forked.append(c)
    cards.extend(forked)

    # Which genes did the corpus actually speak to? Everything else falls through.
    covered = set()
    for c in cards:
        if isinstance(c["matched_on"], list):
            covered.update(c["matched_on"])

    civic = {}
    trials = []
    if network:
        for gene in genes:
            if gene.upper() in covered:
                # Still worth asking CIViC for therapy evidence -- the corpus carries rule
                # sets, not drug annotations, so a gene can be "covered" for prognosis and
                # still have nothing said about treating it.
                hits = [h for h in civic_for_gene(gene) if h["output"] == "therapy"]
            else:
                hits = civic_for_gene(gene)
            if hits:
                civic[gene] = hits

        cond = "acute myeloid leukemia" if disease == "AML" else "myelodysplastic syndrome"
        trials = trials_for(cond, genes)

    unassessed = [
        {
            "gene": v["gene"],
            "variant": v.get("variant"),
            "vaf": v.get("vaf"),
            "reason": "Not in corpus and no CIViC evidence found."
            if network
            else "Not in corpus. Network lookup was disabled, so CIViC was not consulted.",
        }
        for v in ngs
        if v["gene"].upper() not in covered and v["gene"] not in civic
    ]

    return {
        "case_id": case.get("id"),
        "disease_assumed": disease,
        "disease_fork": sorted(implied),
        "fork_note": (
            f"The diagnosis written is {disease}, but a defining lesion implies {', '.join(sorted(implied))}. "
            "Rule sets for BOTH have been loaded. Show the clinician both branches; do not pick one."
            if implied
            else None
        ),
        "genes_submitted": genes,
        "corpus_version": corpus["corpus_version"],
        "network": network,
        "corpus": cards,
        "civic": civic,
        "trials": trials,
        "unassessed": unassessed,
        "valid_citation_ids": sorted(
            [c["id"] for c in cards]
            + [h["id"] for hits in civic.values() for h in hits]
            + [t["id"] for t in trials]
        ),
    }


def infer_disease(marrow_text):
    t = (marrow_text or "").lower()
    if "acute myeloid" in t or "aml" in t:
        return "AML"
    if "myelodysplastic" in t or "mds" in t:
        return "MDS"
    return None


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--case", type=Path, help="Path to a case JSON file")
    ap.add_argument("--genes", help="Comma-separated gene symbols, for a quick lookup")
    ap.add_argument("--disease", help="AML or MDS (used with --genes)")
    ap.add_argument("--no-network", action="store_true", help="Corpus only. No CIViC, no trials.")
    args = ap.parse_args()

    if args.case:
        case = json.loads(args.case.read_text(encoding="utf-8"))
    elif args.genes:
        case = {
            "id": "adhoc",
            "disease": args.disease,
            "ngs": [{"gene": g.strip()} for g in args.genes.split(",")],
        }
    else:
        ap.error("Give me --case or --genes.")

    bundle = retrieve(case, network=not args.no_network)
    json.dump(bundle, sys.stdout, indent=2)
    print()


if __name__ == "__main__":
    main()
