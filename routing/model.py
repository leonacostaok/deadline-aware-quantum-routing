"""Small exact models corresponding to the paper's conditional guarantees.

This is an executable specification, not a router or a quantum speedup demo.
Integer resource accounting avoids floating point feasibility tolerances.
"""
from dataclasses import dataclass
from itertools import product
from math import isfinite, log, sqrt
from typing import Sequence


def natural(value: int, name: str) -> None:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError(f"{name} must be a nonnegative integer")


@dataclass(frozen=True)
class Instance:
    capacities: tuple[int, ...]
    demand_bounds: tuple[int, ...]
    # Each demand has a list of simple path incidence vectors over the links.
    paths: tuple[tuple[tuple[int, ...], ...], ...]
    fixed_load: tuple[int, ...]
    costs: tuple[tuple[int, ...], ...]

    def __post_init__(self):
        e = len(self.capacities)
        if not e or not self.paths:
            raise ValueError("at least one link and demand required")
        if len(self.fixed_load) != e or len(self.demand_bounds) != len(self.paths) or len(self.costs) != len(self.paths):
            raise ValueError("inconsistent dimensions")
        for n in self.capacities + self.demand_bounds + self.fixed_load:
            natural(n, "resource")
        if any(f > c for f, c in zip(self.fixed_load, self.capacities)):
            raise ValueError("fixed load already exceeds capacity")
        for options, costs in zip(self.paths, self.costs):
            if not options or len(options) != len(costs):
                raise ValueError("each demand needs paths and corresponding costs")
            for path in options:
                if len(path) != e or any(type(v) is not int or v not in (0, 1) for v in path) or not any(path):
                    raise ValueError("paths must have nonempty binary incidence")
            if any(type(c) is not int for c in costs):
                raise ValueError("integer costs required")

    @property
    def residual(self):
        return tuple(c - f for c, f in zip(self.capacities, self.fixed_load))

    def validate_choice(self, choice: Sequence[int]):
        if len(choice) != len(self.paths) or any(type(k) is not int or not 0 <= k < len(p) for k, p in zip(choice, self.paths)):
            raise ValueError("invalid route choice")

    def loads(self, choice: Sequence[int]):
        self.validate_choice(choice)
        return tuple(self.fixed_load[e] + sum(d * paths[k][e] for d, paths, k in zip(self.demand_bounds, self.paths, choice)) for e in range(len(self.capacities)))

    def feasible(self, choice: Sequence[int]):
        return all(x <= c for x, c in zip(self.loads(choice), self.capacities))

    def allocations(self):
        return product(*(range(len(p)) for p in self.paths))


@dataclass
class Qubo:
    names: list[str]
    linear: dict[int, int]
    quadratic: dict[tuple[int, int], int]
    offset: int = 0

    def square(self, terms: dict[int, int], constant: int, weight: int):
        self.offset += weight * constant * constant
        items = list(terms.items())
        for i, a in items:
            self.linear[i] = self.linear.get(i, 0) + weight * (a * a + 2 * constant * a)
        for pos, (i, a) in enumerate(items):
            for j, b in items[pos + 1:]:
                key = tuple(sorted((i, j)))
                self.quadratic[key] = self.quadratic.get(key, 0) + 2 * weight * a * b

    def energy(self, bits: Sequence[int]):
        if len(bits) != len(self.names) or any(type(b) is not int or b not in (0, 1) for b in bits):
            raise ValueError("one binary value per variable required")
        return self.offset + sum(a * bits[i] for i, a in self.linear.items()) + sum(a * bits[i] * bits[j] for (i, j), a in self.quadratic.items())


@dataclass
class Encoding:
    instance: Instance
    qubo: Qubo
    route_indices: tuple[tuple[int, ...], ...]
    slack_indices: tuple[tuple[int, ...], ...]
    penalty: int
    objective_range_bound: int

    def residuals(self, bits):
        self.qubo.energy(bits)  # Input validation only.
        out = [sum(bits[i] for i in indices) - 1 for indices in self.route_indices]
        for e, residual in enumerate(self.instance.residual):
            load = sum(self.instance.demand_bounds[d] * self.instance.paths[d][p][e] * bits[i] for d, indices in enumerate(self.route_indices) for p, i in enumerate(indices))
            slack = sum((1 << k) * bits[i] for k, i in enumerate(self.slack_indices[e]))
            out.append(load + slack - residual)
        return tuple(out)

    def decode(self, bits):
        if any(self.residuals(bits)):
            return None
        return tuple(next(p for p, i in enumerate(indices) if bits[i]) for indices in self.route_indices)

    def objective(self, bits):
        return sum(self.instance.costs[d][p] * bits[i] for d, indices in enumerate(self.route_indices) for p, i in enumerate(indices))


def encode(instance: Instance, penalty: int | None = None) -> Encoding:
    # For a linear objective over ALL binary x, range = sum(abs(coefficient)).
    width = sum(abs(c) for row in instance.costs for c in row)
    penalty = width + 1 if penalty is None else penalty
    natural(penalty, "penalty")
    q = Qubo([], {}, {})
    route = []
    for d, paths in enumerate(instance.paths):
        indices = []
        for p, _ in enumerate(paths):
            i = len(q.names)
            q.names.append(f"x_{d}_{p}")
            q.linear[i] = instance.costs[d][p]
            indices.append(i)
        route.append(tuple(indices))
        q.square({i: 1 for i in indices}, -1, penalty)
    slack = []
    for e, residual in enumerate(instance.residual):
        terms = {i: instance.demand_bounds[d] * paths[p][e] for d, paths in enumerate(instance.paths) for p, i in enumerate(route[d])}
        indices = []
        for bit in range(residual.bit_length()):
            i = len(q.names)
            q.names.append(f"s_{e}_{bit}")
            terms[i] = 1 << bit
            indices.append(i)
        slack.append(tuple(indices))
        q.square(terms, -residual, penalty)
    return Encoding(instance, q, tuple(route), tuple(slack), penalty, width)


def exact_minima(encoding: Encoding, max_bits: int = 20):
    n = len(encoding.qubo.names)
    if n > max_bits:
        raise ValueError("exhaustive enumeration limit exceeded")
    best, solutions = None, []
    for bits in product((0, 1), repeat=n):
        energy = encoding.qubo.energy(bits)
        if best is None or energy < best:
            best, solutions = energy, [bits]
        elif energy == best:
            solutions.append(bits)
    return best, solutions


def transition_envelope(instance: Instance, old, new):
    """Exact worst link load in the paper's coherent fluid split model.

    Not a packet-level guarantee: path-delay skew/bursts require extra envelopes.
    """
    instance.validate_choice(old)
    instance.validate_choice(new)
    return tuple(instance.fixed_load[e] + sum(d * max(paths[a][e], paths[b][e]) for d, paths, a, b in zip(instance.demand_bounds, instance.paths, old, new)) for e in range(len(instance.capacities)))


def transition_safe(instance, old, new):
    return all(v <= c for v, c in zip(transition_envelope(instance, old, new), instance.capacities))


def certificate(samples: Sequence[Sequence[float]], costs: Sequence[float], delta: float):
    """Finite, pre-specified policy menu; iid held-out rows within each policy.

    Shared scenarios across policies are allowed. No adaptive reuse guarantee.
    Returns lower bounds and selected policy index, or None for baseline.
    """
    m = len(samples)
    if not m or len(costs) != m or not isfinite(delta) or not 0 < delta < 1:
        raise ValueError("nonempty menu and 0 < delta < 1 required")
    n = len(samples[0])
    if not n or any(len(row) != n for row in samples):
        raise ValueError("equal positive sample counts required")
    if any(not isfinite(v) or not -1 <= v <= 1 for row in samples for v in row):
        raise ValueError("samples must be finite and in [-1, 1]")
    if any(not isfinite(c) or c < 0 for c in costs):
        raise ValueError("costs must be finite and nonnegative")
    radius = sqrt(2 * log(2 * m / delta) / n)
    bounds = tuple(sum(row) / n - radius - c for row, c in zip(samples, costs))
    winner = max(range(m), key=lambda j: bounds[j])
    return bounds, winner if bounds[winner] > 0 else None


def constant_gain(horizon, ready_time, gain_rate, total_cost):
    values = (horizon, ready_time, gain_rate, total_cost)
    if any(not isfinite(v) or v < 0 for v in values) or horizon == 0:
        raise ValueError("finite nonnegative values and positive horizon required")
    return gain_rate * max(horizon - ready_time, 0) - total_cost


def release_check(instance, old, new, expected_version, current_version, now, expires, lower_bound):
    """Pure acceptance predicate; no network writes or certificate estimation.

    The caller must atomically reserve/commit the version and enforce bounds.
    A rejected result does not assert that the baseline is safe after a failure.
    """
    if any(not isfinite(v) for v in (now, expires, lower_bound)):
        return False
    if expected_version != current_version or now >= expires or lower_bound <= 0:
        return False
    return instance.feasible(old) and instance.feasible(new) and transition_safe(instance, old, new)
