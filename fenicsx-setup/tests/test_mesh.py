import numpy as np
import pytest

from biodiff import box_mesh, rectangle_mesh
from biodiff.postprocess import domain_volume


def test_rectangle_area():
    geo = rectangle_mesh(length=2.0, height=3.0, n=4)
    assert domain_volume(geo.mesh) == pytest.approx(6.0)


def test_box_volume():
    geo = box_mesh(length=1.0, width=2.0, height=0.5, n=2)
    assert domain_volume(geo.mesh) == pytest.approx(1.0)


@pytest.mark.parametrize(
    "factory, markers",
    [(rectangle_mesh, {1, 2, 3, 4}), (box_mesh, {1, 2, 3, 4, 5, 6})],
)
def test_all_sides_are_tagged(factory, markers):
    geo = factory(n=4)
    comm = geo.mesh.comm
    local = set(np.unique(geo.facet_tags.values).tolist())
    assert set().union(*comm.allgather(local)) == markers
