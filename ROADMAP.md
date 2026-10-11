# novelty hypothesis and research roadmap

## proposed research claim

can joint selection of the traffic subset, solver and computation budget improve accumulated service quality when optimization results expire, after including all execution and deployment costs?

the integration is the candidate contribution. it is not yet a verified novelty claim. broad quantum routing and demand decomposition overlap prior publications and a published Deutsche Telekom/Fujitsu patent application discussed in the paper

## alternatives and added value

| direction | proposed value | experiment that could disprove it |
|---|---|---|
| classical deadline-aware controller | immediate value without waiting for quantum hardware | compare with a strong classical optimizer at tuned fixed cadences under equal compute budgets |
| conflict-aware demand grouping | spend effort on interacting bottlenecks and keep quantum jobs small | compare with random, geographic and fixed-size grouping; report global objective loss |
| reservation-aware parallel jobs | enforce cross-job resource consistency | compare throughput and fragmentation with centralized optimization and sequential jobs |
| packet-valid transition certificates | bridge the fluid proof to deployable network changes | replay path-delay skew, in-flight traffic and bursts against independently verified arrival envelopes |
| calibrated useful-horizon prediction | avoid spending compute on soon-obsolete states | compare to constant horizons, with held-out episode data and distribution-shift tests |
| backend selection with all costs | identify any regime where a quantum device actually helps | compare the same controller and QUBO using classical and quantum backends, including queue time and fees |
| explicit abstention | prevent weak or late candidates from being deployed | compare service loss and rejected work with always-deploy policies; account for sunk compute costs |
| benchmark and accounting contract | make backend claims reproducible even if no quantum gain appears | reproduce results across independent implementations and report sensitivity to path sets and budgets |

## staged implementation

1. complete independent technical review of the model and proofs
2. implement a classical event-driven simulator with a declared TCP/traffic model, loss metric and update semantics
3. compare continuous-splitting linear optimization where deployable, discrete integer optimization and tuned heuristics
4. build a classical controller for dynamic grouping, reservations, timing and fallback
5. add a quantum adapter using exactly the same path candidates, constraints and accounting boundaries
6. run frozen test workloads and report failures, expired jobs, variance and confidence intervals
7. attempt a limited operator trial only after packet-level assumptions and rollback behavior are verified

## success criteria

report net benefit over time against a strong classical baseline, not just a lower QUBO energy or shorter device-only execution. distinguish controller benefit from hardware benefit by holding the controller fixed while changing only the backend

## stop or redesign conditions

if strong classical methods finish well inside the useful horizon, if quantum access time dominates, if decomposition loses more value than it saves, or if defensible validation cannot certify useful gains, retain the classical control components and revise the quantum hypothesis
