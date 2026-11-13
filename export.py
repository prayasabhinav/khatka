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
print("wrote", sorted(os.listdir(OUT)))
