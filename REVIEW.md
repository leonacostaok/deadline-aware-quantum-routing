# consistency review for v0.1

this is a self-review record, not independent peer review

## revisions made before release

| issue found | correction |
|---|---|
| superposition could be mistaken for observing every route | explicitly distinguish encoded states, samples and classical readout |
| a feasible destination allocation can overload links while installing | add an exact fluid transition envelope and a two-demand swap counterexample |
| a fluid envelope could be read as a packet-level guarantee | state coherent split assumptions and the unresolved in-flight, burst and forwarding consistency obligations |
| separate jobs can consume the same spare capacity | require disjoint demand groups and explicit concurrent capacity reservations |
| non-strict or incorrectly bounded penalties can admit invalid minima | require a strict penalty exceeding the objective range on all binary assignments, including invalid ones |
| a solver optimum could be confused with operational improvement | separate the QUBO surrogate from full-horizon service benefit |
| fallback can hide spent computation cost | charge unsuccessful jobs and include fallback in each complete policy |
| selection after validation creates multiple-comparison bias | use a frozen finite menu and simultaneous Hoeffding bounds |
| repeated decisions can silently exhaust the confidence budget | state conditional fresh-validation assumptions and a summable failure budget |
| later gating can change the certified policy | require gates and costs to be included before validation |
| stale snapshots can invalidate resource and benefit claims | require version-consistent reservations and revisit the certificate after relevant changes |
| qubit counts can imply reliability or speedup | separate binary variables, data qubits, physical overhead, hardware faults and optimization success |
| finite tests could be described as formal verification | distinguish hand proofs, finite regression checks and missing proof-assistant verification |

## verification performed

- all 16 standard-library tests pass locally
- expanded QUBO energies match the squared-residual definition on every assignment of 64 seeded feasible instances
- global QUBO minima match independent feasible-route enumeration for those instances
- the strict-penalty counterexample and infeasible-instance checks behave as stated
- transition envelopes match enumerated corner maxima on the tested instances
- a fully specified iid two-point example has exact false-acceptance probability below the stated confidence budget
- generated JSON and LaTeX results reproduce with `--check`
- the PDF was compiled and visually checked page by page

## proof boundaries

capacity results require actual demand envelopes, valid paths, the specified fluid transition model and enforceable reservations. expected-value results separately require a fixed policy menu and independent validation drawn from the deployment distribution. neither set of assumptions follows from the other

the Python functions cannot validate these physical or statistical premises. the release predicate does not perform atomic commits, deploy network changes or estimate the scenario distribution. QUBO global-minimum claims do not extend to arbitrary heuristic samples

## remaining review and research

independent networking and quantum-optimization review, proof-assistant formalization if desired, representative workload evaluation, packet-valid update bounds, executable solver adapters and measured full-system hardware costs remain outstanding. the preprint makes no claim of publication priority, patentability, quantum advantage or deployment readiness
