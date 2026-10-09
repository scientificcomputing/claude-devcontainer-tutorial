import pytest

from biodiff import TISSUES, Tissue, get_tissue


def test_get_known_tissue():
    tissue = get_tissue("gray_matter")
    assert tissue is TISSUES["gray_matter"]
    assert tissue.diffusion > 0


def test_get_unknown_tissue_raises():
    with pytest.raises(KeyError, match="Unknown tissue"):
        get_tissue("bone")


@pytest.mark.parametrize("diffusion", [0.0, -1.0])
def test_non_positive_diffusion_raises(diffusion):
    with pytest.raises(ValueError):
        Tissue("bad", diffusion=diffusion)


def test_negative_clearance_raises():
    with pytest.raises(ValueError):
        Tissue("bad", diffusion=1.0, clearance=-0.1)


def test_diffusion_time():
    tissue = Tissue("test", diffusion=2.0)
    assert tissue.diffusion_time(4.0) == pytest.approx(8.0)
