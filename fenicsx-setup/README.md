# biodiff

A tiny [FEniCSx](https://fenicsproject.org) toolkit for simulating the transport of
tracers, drugs and metabolites in biological tissue. It solves the linear
reaction–diffusion equation

$$
\frac{\partial u}{\partial t} - \nabla \cdot (D \nabla u) + k u = f
$$

where $u$ is the concentration, $D$ the effective diffusion coefficient and $k$ a
clearance rate. Units are millimetres and seconds.

The package is intentionally small: it's the starting point for a tutorial on
extending a scientific code with Claude Code. See [PROMPT.md](PROMPT.md) for prompts.

## Installation

DOLFINx must already be installed (for example via the
`ghcr.io/fenics/dolfinx/dolfinx` Docker image used in `.devcontainer`). Then run:

```bash
python3 -m pip install -e ".[dev]"
```

## Quick start

Simulate a contrast agent (gadobutrol) entering a 2 mm × 2 mm patch of gray matter
from one side over one hour:

```python
from biodiff import DiffusionSolver, get_tissue, rectangle_mesh, total_amount

geo = rectangle_mesh(length=2.0, height=2.0, n=32)
solver = DiffusionSolver(geo.mesh, get_tissue("gray_matter"), dt=60.0, facet_tags=geo.facet_tags)
solver.add_dirichlet_bc(marker=1, value=1.0)  # concentration 1 at x = 0

for t, u in solver.solve(t_end=3600.0):
    print(f"t = {t / 60:4.0f} min, amount = {total_amount(u):.4f}")
```

## Package layout

| Module | Contents |
| --- | --- |
| `biodiff.materials` | `Tissue` dataclass and a small library of tissue parameters |
| `biodiff.mesh` | Rectangle/box meshes with tagged boundaries (1–6 = x_min, x_max, y_min, …) |
| `biodiff.solver` | `DiffusionSolver`, backward Euler + Lagrange elements |
| `biodiff.postprocess` | Total amount, mean concentration, L2 error |

## Running the tests

```bash
python3 -m pytest
mpirun -n 2 python3 -m pytest   # in parallel
```
