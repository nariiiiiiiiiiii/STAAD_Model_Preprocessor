from math import inf, nan

import pytest

from staadprep.numbering.renumber import NumberingPolicy


@pytest.mark.parametrize("precision", [nan, inf, -inf])
def test_numbering_policy_rejects_nonfinite_precision(precision: float) -> None:
    with pytest.raises(ValueError, match="node_precision_m"):
        NumberingPolicy(node_precision_m=precision)
