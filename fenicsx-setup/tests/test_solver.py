import numpy as np
import pytest
import ufl

from biodiff import DiffusionSolver, Tissue, mean_concentration, rectangle_mesh, total_amount
from biodiff.postprocess import l2_error


def test_invalid_time_step_raises():
    geo = rectangle_mesh(n=2)
    with pytest.raises(ValueError):
        DiffusionSolver(geo.mesh, Tissue("t", diffusion=1.0), dt=0.0)


def test_bc_without_facet_tags_raises():
    geo = rectangle_mesh(n=2)
    solver = DiffusionSolver(geo.mesh, Tissue("t", diffusion=1.0), dt=0.1)
    with pytest.raises(ValueError, match="facet_tags"):
        solver.add_dirichlet_bc(1, 1.0)


def test_mass_is_conserved_without_clearance():
    """With no-flux boundaries and no clearance the total amount is constant."""
    geo = rectangle_mesh(n=8)
    solver = DiffusionSolver(geo.mesh, Tissue("t", diffusion=0.1), dt=0.05)
    solver.set_initial_condition(lambda x: np.exp(-20 * ((x[0] - 0.3) ** 2 + (x[1] - 0.5) ** 2)))

    initial = total_amount(solver.u)
    for _ in solver.solve(t_end=0.5):
        pass

    assert solver.t == pytest.approx(0.5)
    assert total_amount(solver.u) == pytest.approx(initial, rel=1e-10)


def test_uniform_clearance_matches_backward_euler_decay():
    """A uniform field with clearance k decays as (1 + k dt)^(-n) with backward Euler."""
    k, dt, n_steps = 0.5, 0.1, 10
    geo = rectangle_mesh(n=4)
    solver = DiffusionSolver(geo.mesh, Tissue("t", diffusion=1.0, clearance=k), dt=dt)
    solver.set_initial_condition(2.0)

    for _ in range(n_steps):
        solver.step()

    expected = 2.0 * (1 + k * dt) ** (-n_steps)
    assert mean_concentration(solver.u) == pytest.approx(expected, rel=1e-10)


def test_converges_to_linear_steady_state():
    """Fixed concentrations on two opposite sides give a linear steady-state profile."""
    geo = rectangle_mesh(n=8)
    solver = DiffusionSolver(
        geo.mesh,
        Tissue("t", diffusion=1.0),
        dt=10.0,
        facet_tags=geo.facet_tags,
    )
    solver.add_dirichlet_bc(marker=1, value=1.0)  # x = 0
    solver.add_dirichlet_bc(marker=2, value=0.0)  # x = 1
    for _ in solver.solve(t_end=100.0):
        pass

    x = ufl.SpatialCoordinate(geo.mesh)
    assert l2_error(solver.u, 1 - x[0]) < 1e-8
