"""Time dependent reaction-diffusion solver.

Solves

    du/dt - div(D grad u) + k u = f      in the domain
                              u = g      on Dirichlet boundaries
                     D grad u . n = 0    on the remaining boundary

with continuous Lagrange elements in space and the backward Euler method in
time.
"""

from collections.abc import Callable, Iterator

import dolfinx
import dolfinx.fem.petsc
import numpy as np
import ufl

from .materials import Tissue


class DiffusionSolver:
    """Reaction-diffusion solver for a single solute in a single tissue.

    Parameters
    ----------
    mesh:
        The computational mesh.
    tissue:
        Tissue parameters (diffusion coefficient and clearance rate).
    dt:
        Time step in seconds.
    degree:
        Polynomial degree of the Lagrange elements.
    facet_tags:
        Boundary markers, required when using :meth:`add_dirichlet_bc`.
    source:
        Optional source term f (Constant, Function or UFL expression).
    """

    def __init__(
        self,
        mesh: dolfinx.mesh.Mesh,
        tissue: Tissue,
        dt: float,
        degree: int = 1,
        facet_tags: dolfinx.mesh.MeshTags | None = None,
        source=None,
    ) -> None:
        if dt <= 0:
            raise ValueError(f"Time step must be positive, got {dt}")

        self.mesh = mesh
        self.tissue = tissue
        self.facet_tags = facet_tags
        self.V = dolfinx.fem.functionspace(mesh, ("Lagrange", degree))
        self.t = 0.0

        scalar = dolfinx.default_scalar_type
        self.dt = dolfinx.fem.Constant(mesh, scalar(dt))
        self.D = dolfinx.fem.Constant(mesh, scalar(tissue.diffusion))
        self.k = dolfinx.fem.Constant(mesh, scalar(tissue.clearance))

        self.u = dolfinx.fem.Function(self.V, name="concentration")
        self.u_prev = dolfinx.fem.Function(self.V, name="concentration_prev")
        self.bcs: list[dolfinx.fem.DirichletBC] = []

        u, v = ufl.TrialFunction(self.V), ufl.TestFunction(self.V)
        f = source if source is not None else dolfinx.fem.Constant(mesh, scalar(0.0))
        self.a = (
            u * v + self.dt * (self.D * ufl.inner(ufl.grad(u), ufl.grad(v)) + self.k * u * v)
        ) * ufl.dx
        self.L = (self.u_prev + self.dt * f) * v * ufl.dx
        self._problem: dolfinx.fem.petsc.LinearProblem | None = None

    def set_initial_condition(self, value: float | Callable[[np.ndarray], np.ndarray]) -> None:
        """Set the initial concentration from a constant or a function of x."""
        if callable(value):
            self.u_prev.interpolate(value)
        else:
            self.u_prev.x.array[:] = value
        self.u.x.array[:] = self.u_prev.x.array

    def add_dirichlet_bc(self, marker: int, value: float) -> None:
        """Prescribe a fixed concentration on the boundary facets with the given marker."""
        if self.facet_tags is None:
            raise ValueError("facet_tags must be provided to apply boundary conditions")
        fdim = self.mesh.topology.dim - 1
        dofs = dolfinx.fem.locate_dofs_topological(self.V, fdim, self.facet_tags.find(marker))
        bc_value = dolfinx.fem.Constant(self.mesh, dolfinx.default_scalar_type(value))
        self.bcs.append(dolfinx.fem.dirichletbc(bc_value, dofs, self.V))
        self._problem = None  # Rebuild the problem with the new boundary conditions

    def _get_problem(self) -> dolfinx.fem.petsc.LinearProblem:
        if self._problem is None:
            self._problem = dolfinx.fem.petsc.LinearProblem(
                self.a,
                self.L,
                u=self.u,
                bcs=self.bcs,
                petsc_options_prefix=f"biodiff_{id(self)}_",
                petsc_options={"ksp_type": "preonly", "pc_type": "lu"},
            )
        return self._problem

    def step(self) -> dolfinx.fem.Function:
        """Advance the solution one time step and return the new concentration."""
        self._get_problem().solve()
        self.u.x.scatter_forward()
        self.u_prev.x.array[:] = self.u.x.array
        self.t += float(self.dt.value)
        return self.u

    def solve(self, t_end: float) -> Iterator[tuple[float, dolfinx.fem.Function]]:
        """Step until ``t_end``, yielding ``(t, u)`` after each step."""
        dt = float(self.dt.value)
        while self.t < t_end - 1e-12 * dt:
            u = self.step()
            yield self.t, u
