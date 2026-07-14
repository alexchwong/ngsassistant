#!/usr/bin/env python3
"""
Citation verifier. The other half of the guarantee.

retrieve.py controls what evidence reaches the assistant. This script controls what the
assistant is allowed to have done with it: every citation tag in the draft must name
something that was actually retrieved. A tag that matches nothing was invented, and an
invented citation on a gene-prognosis claim is the single worst thing this tool could
produce -- worse than no answer, because it looks exactly like a good one.

It also catches the quieter failure: a gene that was submitted, was never assessed, and
was never mentioned. A silently absent gene is indistinguishable from a gene that was
considered and cleared. The clinician cannot tell those apart, so we make the tool say it.

Usage:
    python retrieve.py --case cases/case1.json > bundle.json
    python verify.py --bundle bundle.json --draft draft.md

Exit code 0 = clean. 1 = something in the draft is not supported. Non-zero means the
draft does not go to the clinician until it is fixed.
"""

import argparse
import json
import re
import sys
from pathlib import Path

# Citation tags look like [eln22-npm1-with-flt3], [CIViC:EID116], [NCT:NCT06696183].
TAG = re.compile(r"\[([A-Za-z0-9:_\-\.]+)\]")

# Words that read as a citation but are not one. Bracketed prose is fine; we only care
# about things shaped like an ID.
IGNORE = {"see", "note", "sic", "todo", "gap", "warning"}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--bundle", type=Path, required=True, help="Evidence bundle from retrieve.py")
    ap.add_argument("--draft", type=Path, required=True, help="The drafted answer (markdown or text)")
    args = ap.parse_args()

    bundle = json.loads(args.bundle.read_text(encoding="utf-8"))
    draft = args.draft.read_text(encoding="utf-8")

    valid = set(bundle.get("valid_citation_ids", []))
    cited = {t for t in TAG.findall(draft) if t.lower() not in IGNORE}

    invented = sorted(cited - valid)
    unused = sorted(valid - cited)

    # Every gene the retriever could not assess must appear by name in the draft. Not
    # buried in a footnote -- named, so the clinician knows the tool looked and found
    # nothing, rather than assuming it looked and was satisfied.
    unassessed = [u["gene"] for u in bundle.get("unassessed", [])]
    unnamed = [g for g in unassessed if g not in draft]

    # Cards drawn from a source we have not yet checked against the primary must carry
    # their stamp into the answer. The clinician is entitled to know which of the claims
    # in front of them are provisional.
    pending = [
        c["id"]
        for c in bundle.get("corpus", [])
        if c["source"].get("provenance") == "secondary_pending_verification" and c["id"] in cited
    ]

    ok = True

    if invented:
        ok = False
        print("FABRICATED CITATIONS -- these tags match nothing that was retrieved:")
        for t in invented:
            print(f"  [{t}]")
        print("  Remove the claim or remove the tag. Do not re-tag it with a different ID.\n")

    if unnamed:
        ok = False
        print("SILENTLY DROPPED GENES -- submitted, not assessed, and not mentioned in the draft:")
        for g in unnamed:
            print(f"  {g}")
        print("  Each must appear in the answer as 'no assessment', with the reason.\n")

    if pending:
        print("PROVISIONAL SOURCES CITED -- the draft must show these are pending verification:")
        for t in pending:
            print(f"  [{t}]")
        print("  Not an error. But the answer must say so where the claim is made.\n")

    if unused:
        print(f"(FYI: {len(unused)} retrieved item(s) not cited. Fine if they were irrelevant.)")
        for t in unused[:10]:
            print(f"  {t}")
        print()

    if ok:
        print(f"CLEAN. {len(cited)} citation(s), all traceable to retrieved evidence.")
        return 0

    print("NOT CLEAN. Fix the above before this goes to a clinician.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
