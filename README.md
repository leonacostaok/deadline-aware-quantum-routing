# deadline aware hybrid optimization for ISP traffic engineering

**research preprint v0.1 — León Acosta — 11 October 2026**

[read the paper (PDF)](paper/paper.pdf) · [LaTeX source](paper/paper.tex) · [review notes](REVIEW.md) · [research roadmap](ROADMAP.md)

an ISP route optimizer has to finish while its answer is still useful. this project proposes choosing traffic subsets, solvers and computation budgets according to the benefit remaining after computation, validation and installation

quantum annealing or QAOA can be candidate generators. a classical acceptance layer checks feasibility, transitions and freshness. the implementation is an executable mathematical specification, not a network controller or a quantum hardware experiment

## what the paper establishes

- an exact worst-case capacity envelope for a stated asynchronous fluid transition model
- safe composition of disjoint jobs with explicit capacity reservations
- a sufficient QUBO penalty: every **global** minimum is feasible and surrogate-optimal when a feasible allocation exists
- a finite-menu expected-improvement certificate using independent, representative validation episodes
- a simple deadline break-even condition, plus counterexamples to stronger claims

the proofs are conditional mathematical arguments, not proof-assistant verification. they do not establish quantum speedup, packet-level safety, global optimality of decomposition or reliable ISP deployment. there is no single defensible physical qubit count without a specified workload and hardware execution model

## reproduce

Python 3.10 or later; no Python dependencies or network access needed

```sh
python3 -m unittest discover -s tests -v
python3 scripts/reproduce.py --check
```

the 16 tests include exhaustive comparison of expanded QUBOs and independently enumerated feasible routes on 64 seeded small instances. the examples include an unsafe route swap, a safe staged alternative, a deadline ranking reversal and confidence-bound arithmetic

regenerate the constructed example outputs with:

```sh
python3 scripts/reproduce.py
```

build the PDF with a TeX installation containing `latexmk`, `pdflatex`, Latin Modern and the packages used in the source:

```sh
make paper
```

`make check` runs the tests, checks deterministic results and builds the paper. all reported numbers are constructed examples, not ISP measurements or quantum performance results

## repository map

| path | purpose |
|---|---|
| `paper/paper.tex` | model, assumptions, proofs, related work and limitations |
| `paper/paper.pdf` | compiled preprint |
| `routing/model.py` | integer QUBO encoder, exact checks, transition and acceptance predicates |
| `tests/test_model.py` | finite regression and counterexample checks |
| `scripts/reproduce.py` | deterministic tables and QUBO export |
| `results/` | generated example data and portable QUBO coefficients |
| `ROADMAP.md` | novelty hypothesis, alternatives and falsifiable experiments |
| `REVIEW.md` | consistency review and remaining obligations |

## research status and attribution

quantum routing, demand decomposition, safe network updates and solver selection already have related work. the proposed distinction is the joint, deadline-sensitive choice of subset, solver and budget with an explicit deployment acceptance contract. its novelty and usefulness remain hypotheses to test

research direction proposed by León Acosta; manuscript and reference implementation developed with assistance from OpenAI ChatGPT/Codex. no independent expert review, QPU experiment or production trial has been completed. bibliographic sources and detailed comparisons are in the paper
