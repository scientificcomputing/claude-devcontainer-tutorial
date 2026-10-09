"""biodiff - a tiny FEniCSx toolkit for reaction-diffusion in biological tissue.

The package solves the linear reaction-diffusion equation

    du/dt - div(D grad u) + k u = f

which is a common model for the transport of tracers (e.g. MRI contrast
agents), drugs and metabolites in tissue.
"""

from importlib.metadata import PackageNotFoundError, version

from .materials import TISSUES, Tissue, get_tissue
from .mesh import box_mesh, rectangle_mesh
from .postprocess import l2_error, mean_concentration, total_amount
from .solver import DiffusionSolver

try:
    __version__ = version("biodiff")
except PackageNotFoundError:  # pragma: no cover
    __version__ = "0.0.0"

__all__ = [
    "TISSUES",
    "DiffusionSolver",
    "Tissue",
    "box_mesh",
    "get_tissue",
    "l2_error",
    "mean_concentration",
    "rectangle_mesh",
    "total_amount",
]
