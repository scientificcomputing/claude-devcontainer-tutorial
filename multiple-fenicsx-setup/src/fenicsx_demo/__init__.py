"""fenicsx_demo - a placeholder package for running the same code against
several DOLFINx versions (stable and nightly)."""

from importlib.metadata import PackageNotFoundError, version

import dolfinx
import ufl
from mpi4py import MPI

try:
    __version__ = version("fenicsx-demo")
except PackageNotFoundError:  # pragma: no cover
    __version__ = "0.0.0"

__all__ = ["dolfinx_version", "unit_square_area"]


def dolfinx_version() -> str:
    """Return the version of the DOLFINx installation in use."""
    return dolfinx.__version__


def unit_square_area(n: int = 8, comm: MPI.Comm = MPI.COMM_WORLD) -> float:
    """Compute the area of the unit square by assembling ``1 * dx``.

    The result is summed over all MPI ranks, so it is 1 in serial and in parallel.
    """
    mesh = dolfinx.mesh.create_unit_square(comm, n, n)
    one = dolfinx.fem.Constant(mesh, dolfinx.default_scalar_type(1.0))
    local = dolfinx.fem.assemble_scalar(dolfinx.fem.form(one * ufl.dx))
    return mesh.comm.allreduce(local, op=MPI.SUM)
