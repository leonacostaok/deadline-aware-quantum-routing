import math
import random
import unittest
from itertools import product

from routing.model import Instance, certificate, constant_gain, encode, exact_minima, release_check, transition_envelope, transition_safe


def swap_instance():
    return Instance((1, 1, 1), (1, 1), (((1, 0, 0), (0, 1, 0), (0, 0, 1)),) * 2, (0, 0, 0), ((0, 0, 0),) * 2)


def generated_instances(count=64):
    rng = random.Random(1729)
    cases = []
    while len(cases) < count:
        paths = tuple(tuple((1, 0) if rng.randrange(2) else (0, 1) for _ in range(2)) for _ in range(2))
        case = Instance(tuple(rng.randint(1, 3) for _ in range(2)), tuple(rng.randint(1, 2) for _ in range(2)), paths, (0, 0), tuple(tuple(rng.randint(-3, 4) for _ in range(2)) for _ in range(2)))
        if any(case.feasible(c) for c in case.allocations()):
            cases.append(case)
    return cases


class EncodingTests(unittest.TestCase):
    def test_expanded_polynomial_and_global_minima(self):
        for instance in generated_instances():
            enc = encode(instance)
            for bits in product((0, 1), repeat=len(enc.qubo.names)):
                self.assertEqual(enc.qubo.energy(bits), enc.objective(bits) + enc.penalty * sum(r * r for r in enc.residuals(bits)))
            optimum, minima = exact_minima(enc)
            independent = min(sum(instance.costs[d][p] for d, p in enumerate(c)) for c in instance.allocations() if instance.feasible(c))
            self.assertEqual(optimum, independent)
            for bits in minima:
                choice = enc.decode(bits)
                self.assertIsNotNone(choice)
                self.assertTrue(instance.feasible(choice))

    def test_penalty_must_be_strict(self):
        instance = Instance((1,), (1,), (((1,),),), (0,), ((2,),))
        enc = encode(instance, penalty=2)
        _, minima = exact_minima(enc)
        self.assertTrue(any(enc.decode(bits) is None for bits in minima))
        enc = encode(instance)
        self.assertTrue(all(enc.decode(bits) is not None for bits in exact_minima(enc)[1]))

    def test_infeasible_model_cannot_be_fixed_by_penalty(self):
        enc = encode(Instance((0,), (1,), (((1,),),), (0,), ((0,),)))
        self.assertTrue(all(enc.decode(bits) is None for bits in exact_minima(enc)[1]))

    def test_zero_residual_needs_no_slack_bit(self):
        enc = encode(Instance((0, 1), (1,), (((0, 1),),), (0, 0), ((0,),)))
        self.assertEqual(enc.slack_indices[0], ())
        self.assertTrue(all(enc.decode(bits) == (0,) for bits in exact_minima(enc)[1]))

    def test_fixed_load_and_residual(self):
        inst = Instance((4, 2), (2,), (((1, 0), (0, 1)),), (3, 0), ((0, 3),))
        self.assertFalse(inst.feasible((0,)))
        self.assertTrue(inst.feasible((1,)))
        self.assertTrue(all(encode(inst).decode(b) == (1,) for b in exact_minima(encode(inst))[1]))

    def test_validation_and_size_guard(self):
        with self.assertRaises(ValueError):
            Instance((1,), (-1,), (((1,),),), (0,), ((0,),))
        with self.assertRaises(ValueError):
            Instance((1,), (1,), (((1,),),), (2,), ((0,),))
        enc = encode(swap_instance())
        with self.assertRaises(ValueError):
            enc.qubo.energy([0.5] * len(enc.qubo.names))
        with self.assertRaises(ValueError):
            exact_minima(enc, max_bits=1)


class TransitionTests(unittest.TestCase):
    def test_endpoint_feasibility_does_not_imply_transition_safety(self):
        inst = swap_instance()
        self.assertTrue(inst.feasible((0, 1)))
        self.assertTrue(inst.feasible((1, 0)))
        self.assertFalse(transition_safe(inst, (0, 1), (1, 0)))
        self.assertEqual(transition_envelope(inst, (0, 1), (1, 0)), (2, 2, 0))

    def test_temporary_path_allows_three_safe_stages(self):
        inst = swap_instance()
        stages = [(0, 1), (2, 1), (2, 0), (1, 0)]
        self.assertTrue(all(transition_safe(inst, a, b) for a, b in zip(stages, stages[1:])))

    def test_envelope_is_exact_worst_case_per_link(self):
        for inst in generated_instances(16):
            for old in inst.allocations():
                for new in inst.allocations():
                    envelope = transition_envelope(inst, old, new)
                    corners = [inst.loads(tuple(new[i] if b else old[i] for i, b in enumerate(bits))) for bits in product((0, 1), repeat=len(old))]
                    self.assertEqual(envelope, tuple(max(c[e] for c in corners) for e in range(len(inst.capacities))))

    def test_shared_link_counted_once_in_fluid_model(self):
        inst = Instance((1, 1, 1), (1,), (((1, 1, 0), (1, 0, 1)),), (0, 0, 0), ((0, 0),))
        self.assertEqual(transition_envelope(inst, (0,), (1,)), (1, 1, 1))


class DecisionTests(unittest.TestCase):
    def test_delay_can_reverse_ranking(self):
        self.assertGreater(constant_gain(30, 2, 0.1, 0.2), constant_gain(30, 25, 0.3, 0.2))
        self.assertLess(constant_gain(30, 35, 0.3, 0.2), 0)

    def test_positive_certificate_and_abstention(self):
        bounds, chosen = certificate([[0.4] * 1000, [0.1] * 1000], [0.05, 0.05], 0.05)
        self.assertEqual(chosen, 0)
        self.assertGreater(bounds[0], 0)
        self.assertEqual(certificate([[0.01] * 100], [0], 0.05)[1], None)

    def test_exact_false_acceptance_probability(self):
        # A fully specified iid +/-1 distribution with negative expected gain.
        n, p, delta = 80, 0.45, 0.05
        false_accept = 0.0
        for k in range(n + 1):
            if certificate([[1.0] * k + [-1.0] * (n - k)], [0], delta)[1] is not None:
                false_accept += math.comb(n, k) * p**k * (1 - p)**(n-k)
        self.assertLessEqual(false_accept, delta)

    def test_menu_correction_and_cost(self):
        lower1 = certificate([[0.4] * 1000], [0], 0.05)[0][0]
        lower2 = certificate([[0.4] * 1000] * 2, [0, 0], 0.05)[0][0]
        self.assertLess(lower2, lower1)
        self.assertIsNone(certificate([[0.4] * 1000], [0.5], 0.05)[1])

    def test_bad_statistics_rejected(self):
        for samples, costs, delta in [([], [], 0.05), ([[]], [0], 0.05), ([[float('nan')]], [0], 0.05), ([[2]], [0], 0.05), ([[0]], [-1], 0.05), ([[0]], [0], 1), ([[0], [0, 0]], [0, 0], 0.05)]:
            with self.assertRaises(ValueError):
                certificate(samples, costs, delta)

    def test_stale_expired_unsafe_and_nonpositive_results_rejected(self):
        inst = swap_instance()
        args = (inst, (0, 1), (2, 1), 7, 7, 5, 10, 0.1)
        self.assertTrue(release_check(*args))
        self.assertFalse(release_check(inst, (0, 1), (2, 1), 7, 8, 5, 10, 0.1))
        self.assertFalse(release_check(inst, (0, 1), (2, 1), 7, 7, 10, 10, 0.1))
        self.assertFalse(release_check(inst, (0, 1), (1, 0), 7, 7, 5, 10, 0.1))
        self.assertFalse(release_check(inst, (0, 1), (2, 1), 7, 7, 5, 10, 0))


if __name__ == '__main__':
    unittest.main()
