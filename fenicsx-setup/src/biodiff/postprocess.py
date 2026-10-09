"""Quantities of interest computed from a concentration field."""

import dolfinx
import ufl
from mpi4py import MPI


def _assemble_scalar(form: ufl.Form, comm: MPI.Comm) -> float:
    local = dolfinx.fem.assemble_scalar(dolfinx.fem.form(form))
    return comm.allreduce(local, op=MPI.SUM)


def total_amount(u: dolfinx.fem.Function) -> float:
    """Total amount of solute, i.e. the integral of u over the domain."""
    return _assemble_scalar(u * ufl.dx, u.function_space.mesh.comm)


def domain_volume(mesh: dolfinx.mesh.Mesh) -> float:
    """Volume (or area in 2D) of the domain."""
    one = dolfinx.fem.Constant(mesh, dolfinx.default_scalar_type(1.0))
    return _assemble_scalar(one * ufl.dx(domain=mesh), mesh.comm)


def mean_concentration(u: dolfinx.fem.Function) -> float:
    """Average concentration over the domain."""
    return total_amount(u) / domain_volume(u.function_space.mesh)


def l2_error(u: dolfinx.fem.Function, u_exact) -> float:
    """L2 norm of u - u_exact, where u_exact is a Function, Constant or UFL expression."""
    diff = u - u_exact
    return _assemble_scalar(ufl.inner(diff, diff) * ufl.dx, u.function_space.mesh.comm) ** 0.5
