"""Original finite exact countermodels, not observations about foreign engines."""

from fractions import Fraction


def test_pairwise_complete_correlations_need_a_matrix_level_contract():
    rows = [
        (-1, -1, None),
        (1, 1, None),
        (-1, None, -1),
        (1, None, 1),
        (None, -1, 1),
        (None, 1, -1),
    ]
    matrix = []
    for left in range(3):
        row = []
        for right in range(3):
            pairs = [
                (r[left], r[right])
                for r in rows
                if r[left] is not None and r[right] is not None
            ]
            x_mean = Fraction(sum(x for x, _ in pairs), len(pairs))
            y_mean = Fraction(sum(y for _, y in pairs), len(pairs))
            xx = sum((x - x_mean) ** 2 for x, _ in pairs)
            yy = sum((y - y_mean) ** 2 for _, y in pairs)
            xy = sum((x - x_mean) * (y - y_mean) for x, y in pairs)
            assert xx == yy  # This literal fixture has equal paired scales.
            row.append(xy / xx)
        matrix.append(row)
    assert matrix == [[1, 1, 1], [1, 1, -1], [1, -1, 1]]
    direction = [-1, 1, 1]
    quadratic = sum(
        direction[i] * matrix[i][j] * direction[j] for i in range(3) for j in range(3)
    )
    assert quadratic == -3
    # An actual correlation matrix must be positive semidefinite. Local
    # pairwise validity does not justify passing this to every covariance API.


def test_weighted_mean_requires_a_shared_pair_mask_and_weight_support():
    observations = [(10, 1), (None, 3)]
    valid = [
        (value, weight)
        for value, weight in observations
        if value is not None and weight is not None
    ]
    total = sum(value * weight for value, weight in valid)
    correct = Fraction(total, sum(weight for _, weight in valid))
    different_domain = Fraction(total, sum(weight for _, weight in observations))
    assert correct == 10
    assert different_domain == Fraction(5, 2)
    assert Fraction(0 * (-1) + 10 * 2, -1 + 2) == 20
    # Negative weights invalidate the range law for a convex weighted mean.


def test_label_alignment_and_positional_pairing_describe_different_computations():
    left = [("A", 1), ("B", 10)]
    right = [("B", 100), ("C", 1000)]
    positional = [a + b for (_, a), (_, b) in zip(left, right)]
    left_map, right_map = dict(left), dict(right)
    aligned = {
        label: left_map[label] + right_map[label]
        if label in left_map and label in right_map
        else None
        for label in left_map.keys() | right_map.keys()
    }
    assert positional == [101, 1010]
    assert aligned == {"A": None, "B": 110, "C": None}


def test_join_multiplicity_changes_downstream_totals_without_a_cardinality_contract():
    measurements = [("A", 1), ("A", 2)]
    annotations = [("A", "red"), ("A", "blue")]
    joined = [
        (amount, label)
        for key, amount in measurements
        for other, label in annotations
        if key == other
    ]
    assert len(joined) == 4
    assert sum(amount for amount, _ in joined) == 6
    assert sum(amount for _, amount in measurements) == 3
