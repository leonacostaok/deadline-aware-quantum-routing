"""Deterministic illustrative results, not empirical ISP or QPU measurements."""
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from routing.model import Instance, certificate, constant_gain, encode, exact_minima, transition_envelope, transition_safe

root = Path(__file__).resolve().parents[1]
instance = Instance((2, 2), (1, 1), (((1, 0), (0, 1)),) * 2, (0, 0), ((0, 1), (0, 2)))
enc = encode(instance)
energy, minima = exact_minima(enc)
swap = Instance((1, 1, 1), (1, 1), (((1, 0, 0), (0, 1, 0), (0, 0, 1)),) * 2, (0, 0, 0), ((0, 0, 0),) * 2)
stages = [(0, 1), (2, 1), (2, 0), (1, 0)]
lower, chosen = certificate([[0.4] * 1000, [0.1] * 1000], [0.05, 0.05], 0.05)
results = {
    'kind': 'constructed examples; no quantum hardware or real traffic measurements',
    'qubo': {'variables': len(enc.qubo.names), 'states_enumerated': 2**len(enc.qubo.names), 'penalty': enc.penalty, 'minimum_energy': energy, 'minimizer_count': len(minima), 'all_minima_feasible': all(enc.decode(b) is not None for b in minima)},
    'transition': {'endpoint_allocations_feasible': all(swap.feasible(c) for c in [(0, 1), (1, 0)]), 'direct_envelope': transition_envelope(swap, (0, 1), (1, 0)), 'direct_safe': transition_safe(swap, (0, 1), (1, 0)), 'staged_safe': all(transition_safe(swap, a, b) for a, b in zip(stages, stages[1:]))},
    'deadline': {'fast_net_loss_seconds': constant_gain(30, 2, 0.1, 0.2), 'slow_net_loss_seconds': constant_gain(30, 25, 0.3, 0.2), 'expired_net_loss_seconds': constant_gain(30, 35, 0.3, 0.2)},
    'certificate': {'n': 1000, 'menu_size': 2, 'delta': 0.05, 'lower_bounds': list(lower), 'selected': chosen},
}
outputs = {
    root/'results/examples.json': json.dumps(results, indent=2, sort_keys=True)+'\n',
    root/'results/qubo.json': json.dumps({'variables': enc.qubo.names, 'offset': enc.qubo.offset, 'linear': [{'i': i, 'bias': v} for i,v in sorted(enc.qubo.linear.items())], 'quadratic': [{'i': i, 'j': j, 'bias': v} for (i,j),v in sorted(enc.qubo.quadratic.items())]}, indent=2)+'\n',
    root/'paper/results.tex': '\n'.join([
        r'\newcommand{\ExampleVariables}{'+str(len(enc.qubo.names))+'}',
        r'\newcommand{\ExampleStates}{'+str(2**len(enc.qubo.names))+'}',
        r'\newcommand{\FastGain}{'+f"{results['deadline']['fast_net_loss_seconds']:.1f}"+'}',
        r'\newcommand{\SlowGain}{'+f"{results['deadline']['slow_net_loss_seconds']:.1f}"+'}',
        r'\newcommand{\CertificateBound}{'+f'{lower[0]:.4f}'+'}',
    ])+'\n',
}
for path, data in outputs.items():
    if '--check' in sys.argv:
        if not path.exists() or path.read_text() != data:
            raise SystemExit(f'results out of date: {path.relative_to(root)}')
    else:
        path.write_text(data)
print(json.dumps(results, indent=2))
