import math
import unittest

from real_data_common import (
    cumulative_case_relative_variance_bound,
    generation_horizon_to_weeks,
    close_budget,
)


class RevisionTests(unittest.TestCase):
    def test_cumulative_case_bound_uses_case_count_not_parent_count(self):
        # R=1.1, k=1, epsilon=0.1: C >= R^2(1+R/k)/epsilon^2.
        expected = 1.1**2 * (1 + 1.1) / 0.1**2
        self.assertAlmostEqual(
            cumulative_case_relative_variance_bound(1.1, 1.0, 0.1), expected
        )

    def test_generation_horizon_conversion(self):
        self.assertAlmostEqual(generation_horizon_to_weeks(22.1, 5.5), 22.1 * 5.5 / 7)

    def test_budget_closes_with_signed_residual(self):
        values = close_budget(0.097, 0.076, 0.005, -0.006, 0.828)
        self.assertAlmostEqual(sum(values), 1.0)
        self.assertLess(values[-1], 1.0)


if __name__ == "__main__":
    unittest.main()
