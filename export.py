"""Writes khatka's data from boardgameBuilder: the blocks, and the pairs known games put together.

Run from the boardgameBuilder folder: python3 khatka/export.py
properties.json, clash-votes.jsonl and keys.jsonl are copied as they are from review-model/.
"""
import json, os, shutil, sys

sys.path.insert(0, "review-model")
from sheet import seen_pairs, DIMENSIONS

OUT = "khatka/data"
partners = [d for d in DIMENSIONS[1:] if d["id"] != "kind-of-fun"]
json.dump({"core": [{"id": b["id"], "name": b["display"]} for b in DIMENSIONS[0]["blocks"]],
           "partners": [{"id": b["id"], "name": b["display"], "slot": d["display"]} for d in partners for b in d["blocks"]]},
          open(f"{OUT}/blocks.json", "w"), indent=1, ensure_ascii=False)
json.dump(sorted(map(list, seen_pairs())), open(f"{OUT}/known-pairs.json", "w"), indent=0)
for f in ("properties.json", "clash-votes.jsonl", "keys.jsonl"):
    shutil.copy(f"review-model/{f}", f"{OUT}/{f}")
# the labels on its uncertain pairs, with whether a source's copied words were found (review-model/label-eval.py --check)
found = json.load(open("review-model/source-labels-checked.json"))
with open(f"{OUT}/new-labels.jsonl", "w") as f:
    for name in sorted(__import__("glob").glob("review-model/source-labels-*.jsonl")):
        for r in map(json.loads, open(name)):
            if r["label"] in ("holds", "clashes"):
                f.write(json.dumps({"pair": r["pair"], "label": r["label"], "settled": bool(found.get(r["pair"])), "basis": r["basis"], "source": r.get("stem", ""), "page": r.get("page", ""), "words": r.get("words", ""), "reason": r.get("reason", "")}, ensure_ascii=False) + "\n")
print("wrote", sorted(os.listdir(OUT)))
