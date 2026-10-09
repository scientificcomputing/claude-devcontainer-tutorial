import pytest

from fenicsx_demo import dolfinx_version, unit_square_area


def test_dolfinx_version():
    assert dolfinx_version()


@pytest.mark.parametrize("n", [1, 4, 16])
def test_unit_square_area(n):
    assert unit_square_area(n) == pytest.approx(1.0)
