"""khatka: the probability that two blocks of a board game design cannot both be true of one game, and the pairs to show a teacher.

A pair is a core mechanic and a block from another part of the design. Two things come out for every pair:

- a flag with its reason, when the table in data/properties.json says the partner contradicts something the core mechanic makes
  or settles. A pair a known game puts together is never flagged, and a key of mine on a pair outranks the table.
- p, the probability that the two clash: a logistic regression on the table's properties, fitted to data/clash-votes.jsonl,
  where three readers were asked of each of 720 pairs whether both blocks can be true of the same game, and a pair's label is
  the share who said no (unsure counts half). Keys of mine in data/keys.jsonl outrank the readers (r 1, f 0).

No language model runs. The flag never stops a student: in boardgameBuilder the pair can still be placed, and the teacher sees it.

  python3 khatka.py                       writes khatka.json: every pair's p, and the flagged pairs with their reasons
  python3 khatka.py <core> <block>        prints one pair's p and reason, e.g. python3 khatka.py trick-taking fully-cooperative
"""
import json, math, os, sys

DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
load = lambda name: json.load(open(os.path.join(DATA, name)))
lines = lambda name: [json.loads(l) for l in open(os.path.join(DATA, name)) if l.strip()]

BLOCKS = load("blocks.json")
NAME = {b["id"]: b["name"] for b in BLOCKS["core"] + BLOCKS["partners"]}
P = load("properties.json")
PH, MAKES = P["phrases"], P["makes"]
SEEN = {tuple(p) for p in load("known-pairs.json")}
KEYS = {(r["core"], r["block"]): (r["key"], r.get("by", "Prayas")) for r in lines("keys.jsonl")}
VOTES = {tuple(r["pair"].split("+")): r["share_no"] for r in lines("clash-votes.jsonl")}


def reason(c, b):
    """Why the two cannot both hold, or '' when nothing in the table says so."""
    hit = [t for t in P["partners"].get(b, {}).get("clashes", []) if t in MAKES[c]]
    return f"{NAME[c]} {PH[hit[0]]}, and {NAME[b]} says otherwise" if hit else ""


def features(c, b):
    f = {f"b:{b}": 1, "bias": 1, "table": 1 if reason(c, b) else 0}
    for t in MAKES[c]:
        f[f"{t}|{b}"] = f[f"t:{t}"] = 1
    return f


def prob(w, x):
    return 1 / (1 + math.exp(-sum(w.get(k, 0) * v for k, v in x.items())))


def fit(rows):
    """Logistic regression on soft labels (a share between 0 and 1), with a light L2 penalty."""
    w = {}
    for _ in range(3000):
        g = {k: 0.0005 * v for k, v in w.items()}
        for x, y in rows:
            e = prob(w, x) - y
            for k, v in x.items():
                g[k] = g.get(k, 0) + e * v / len(rows)
        for k, v in g.items():
            w[k] = w.get(k, 0) - v
    return w


def flag(c, b):
    k, by = KEYS.get((c, b), (None, None))
    if by == "Prayas":
        return "a teacher has marked this pair for a look" if k == "r" else ""
    return "" if (c, b) in SEEN else reason(c, b)


labelled = VOTES | {p: int(k == "r") for p, (k, by) in KEYS.items() if by == "Prayas" and k != "?"}
W = fit([(features(*p), y) for p, y in labelled.items()])

if __name__ == "__main__":
    if len(sys.argv) == 3:
        c, b = sys.argv[1:]
        print(f"p = {prob(W, features(c, b)):.3f}  {flag(c, b) or 'not flagged'}")
    else:
        pairs = [(c["id"], b["id"]) for c in BLOCKS["core"] for b in BLOCKS["partners"]]
        reasons = {f"{c}+{b}": r for c, b in pairs if (r := flag(c, b))}
        json.dump({"flagged": list(reasons), "reasons": reasons, "p_clash": {f"{c}+{b}": round(prob(W, features(c, b)), 3) for c, b in pairs}},
                  open("khatka.json", "w"), indent=1)
        print(f"wrote khatka.json: {len(reasons)} of {len(pairs)} pairs flagged")
