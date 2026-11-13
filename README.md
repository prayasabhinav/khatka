# khatka

*Version 0.1.0, 13 November 2026. AGPL-3.0.*

khatka reads two blocks of a board game design and gives the probability that they cannot both be true of one game. It runs in [boardgameBuilder](https://boardgame.syntax.prayasabhinav.net), my tool for designing a board game out of blocks, where students in a class place a core mechanic beside blocks from other parts of a game. When the two blocks of a pair contradict each other, the teacher's page shows the pair with a reason and the probability. The student is never stopped. The pair can stay on the canvas, since an unusual pair is sometimes what makes a game new.

A *khatka* is the small misgiving that something is off. Here it is a doubt raised for the teacher.

## What it gives

For each pair of a core mechanic (72 of them) and a block from another part of the design (79), so 5,688 pairs:

- **p**, the probability that the two clash. For example, *pie rule* with *playing alone* gets 0.544; *trick-taking* with *fully cooperative* gets 0.008.
- **a flag and its reason**, when the table of properties says the partner contradicts something the core mechanic makes or settles: *pie rule needs other players, and playing alone says otherwise*. 194 pairs are flagged. A pair that a known game puts together is never flagged.

The flag comes from the table and the probability from the model, so they can differ. The flagged pairs run from 8% to 94%, and four pairs the table leaves alone score 50% or more.

## How it works

No language model runs. khatka is a logistic regression over the table's properties: what each core mechanic makes or settles (`data/properties.json`, under `makes`) and what each partner block clashes with (`partners`).

It learns from `data/clash-votes.jsonl`. For 720 pairs, three readers, each a separate run of Claude Opus, were asked whether both blocks can be true of the same game, and each gave a reason. A pair's label is the share who said no, with an unsure answer counting half: 684 pairs got three yeses, 19 got three noes and 17 were split. A key of mine on a pair outranks both the readers and the table. Keys are in `data/keys.jsonl`, with r counting as 1 and f as 0. None of the 720 keys there yet is mine: they are marked `pattern read`, and khatka does not use them.

Measured on pairs held out of fitting: Brier score 0.0116, and a correlation of 0.80 with the readers' share. Where it put a pair near 85%, readers said no 81% of the time.

It follows the [NSM syntax](https://syntax.prayasabhinav.net/nsm/), as one of the NSMs (Narrow Small Models) listed in [ungli](https://ungli.syntax.prayasabhinav.net): it scores, reads numbers, answers with a number, starts from nothing and learns from another model's labels.

## Use

Python 3.9 or later, nothing to install.

```
python3 khatka.py                              writes khatka.json: every pair's p, and the flagged pairs with their reasons
python3 khatka.py pie-rule playing-alone       prints one pair's p and reason
```

It fits on each run, in about two seconds. The block names are the ids in `data/blocks.json`.

`export.py` rewrites `data/` from a copy of boardgameBuilder, run from that folder as `python3 khatka/export.py`. Kinds of fun are left out on purpose: a kind of fun is the enjoyment a game aims at, and it cannot contradict how the game is played.

## What it does not do

It knows nothing about a pair outside the table's properties and the blocks it was fitted on. A block added to boardgameBuilder after this release has no weights of its own until khatka is fitted again. The table was drawn up from a reading of the pairs known games show, which I asked for in place of keying 720 pairs myself, so its agreement with the readers (704 of 720) shows consistency only; the table and the readers are not independent. Only more keys of mine would let the probability say something the table does not.
