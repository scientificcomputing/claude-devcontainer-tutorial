# Prompts for extending `biodiff` with Claude Code

Each prompt below is meant to be pasted into Claude Code from the repository root.
They're grouped by difficulty, and each one adds a feature that researchers working
on biomedical applications often need. Every prompt asks for tests, so the test suite
grows along with the package.

Before starting the first time you might want to run
```
/init
```
so that `claude` can create `CLAUDE.md`.

Use
```
/clear
```
to start a new session

Use
```
/btw
```
To ask questions about the session without interrupting.

Use
```
/plugins
```
to manage plugins. Sometimes I have found that I need to do
```
/reload-plugins
```
in order for the plugins to take effect.

Use
```
/context
```
To check the amount of tokens used for this context. If you have used a lot of toxens and want to continue the session you should do
```
/compact
```

T

## Tips for writing good prompts

- **Give the physics.** State the equation, units and boundary conditions. Don't
  leave Claude to guess what a "realistic" model means.
- **Say how you'll check the result.** For example: "the total amount must be
  conserved", "the result must converge at second order", or "the result must match
  the analytical solution to 1e-8". Claude can then verify its own work.
- **Point to existing code.** For example: "follow the style of `biodiff/mesh.py`"
  or "reuse `_assemble_scalar`".
- **Ask for a plan first** on larger tasks ("Plan this before you write code"), or
  use plan mode (`Shift+Tab`).
- **Keep it parallel-safe.** FEniCSx code runs under MPI, so ask for tests to pass
  with `mpirun -n 2 python3 -m pytest`.

---

## Level 1: Warm-up

### 1.1 Save results for ParaView

```text
Add a module `biodiff/io.py` with a context-manager class `ResultWriter` that writes
the concentration to a VTX (.bp) file using `dolfinx.io.VTXWriter`, so I can open it
in ParaView. Add an optional `writer` argument to `DiffusionSolver.solve` that writes
after every time step. Add a test that writes a few steps to a temporary directory
and checks that the output exists. Update the README with an example.
```

### 1.2 Quantities of interest in a region

```text
In our tracer studies we compare simulations with MRI. In MRI, people draw regions
of interest (ROIs), such as a patch of gray matter or a region near the ventricles,
and report how the tracer amount and the mean concentration in each region change
over time. I'd like biodiff to support the same kind of analysis.

I haven't decided what the API should look like. For example: how ROIs should be
defined (geometric predicates, existing cell tags, or both), whether quantities
should be computed one at a time or collected over a whole simulation, and how this
fits with `solver.solve()` and `ResultWriter`. Help me work out the design before
writing any code. Ask me questions where the choice is mine.

Whatever we choose must:
- be MPI-safe (reuse `_assemble_scalar` from postprocess.py) and pass under
  `mpirun -n 2 python3 -m pytest`
- be tested against exact results in the existing style, e.g. a uniform field
  over a half-domain ROI, or mass conservation summed over ROIs that cover the
  whole domain
```

### 1.3 A command line interface

```text
Add a command line interface `biodiff-run` (registered in pyproject.toml under
[project.scripts]) that reads a TOML config file containing the mesh size, tissue
name, dt, t_end and Dirichlet boundary conditions. It should run the simulation and
write a CSV of time against total amount. Add an example config in `examples/` and a
test that runs the CLI on a tiny problem.
```

---

## Level 2: Better biomedical models

### 2.1 Heterogeneous tissue (gray and white matter)

```text
Extend DiffusionSolver so the diffusion coefficient and clearance rate can vary in
space. Accept either a single Tissue (current behaviour) or a dict mapping cell-tag
markers to Tissue objects together with a `cell_tags` MeshTags. Represent D and k as
DG0 functions. Keep the existing API backwards compatible. Add tests:
(1) with identical tissues in both subdomains, the result matches the
    single-tissue solver;
(2) mass is still conserved with no-flux boundaries and zero clearance.
```

### 2.2 Permeable boundaries (Robin condition)

```text
In the brain, tracer is exchanged between tissue and the surrounding cerebrospinal
fluid across the pial membrane. Add `DiffusionSolver.add_robin_bc(marker,
permeability, outside_concentration)`, which implements
-D grad(u)·n = permeability * (u - outside_concentration) on the facets with the
given marker, using a `ds` measure with subdomain data. Add tests showing that
(1) as the permeability gets very large, the solution approaches the Dirichlet
    solution;
(2) a uniform initial field equal to the outside concentration stays constant.
```

### 2.3 Time-dependent boundary concentration (intrathecal injection)

```text
After an intrathecal injection, the tracer concentration in the CSF rises and then
decays. Make the Dirichlet and Robin boundary values accept a callable g(t) as well as
a float, and update them at every time step. Add `biodiff/injection.py` with a
bi-exponential bolus model g(t) = c0 * (exp(-t/tau_decay) - exp(-t/tau_rise)) and
sensible default time constants (in seconds) for human CSF. Test it with a
manufactured solution that is spatially uniform but varies in time.
```

### 2.4 Anisotropic diffusion along white matter fibres

```text
Diffusion in white matter is faster along the axons than across them. Add support for
a diffusion tensor D = d_perp * I + (d_par - d_perp) * outer(a, a), where `a` is a
unit fibre direction given as a constant vector or a vector-valued Function (such as
data from DTI). Add a `fibre_tissue(d_par, d_perp, direction)` helper. Test that in
2D, with fibres along x, a Gaussian initial blob spreads further in x than in y, and
that with d_par == d_perp the result matches isotropic diffusion.
```

### 2.5 Synthetic MRI signal

```text
Add `biodiff/mri.py`, which converts concentration into what an MRI scanner would
see. Use the T1 relaxation model 1/T1 = 1/T1_0 + r1 * c, with typical values for
gray matter at 3T and for gadobutrol's relaxivity. Then convert T1 to a normalised
signal with the spoiled gradient echo (SPGR) equation, given the flip angle and TR.
Support both numpy arrays and dolfinx Functions. Test the limits: c = 0 gives
T1 = T1_0, and the signal increases monotonically with concentration.
```

---

## Level 3: Research-grade features

### 3.1 Brain-like geometry with Gmsh

```text
Add `biodiff/geometry.py` with a function that uses the gmsh Python API to build an
idealised 2D brain slice: an outer ellipse (the pial surface) with an inner elliptical
hole (a ventricle), and an inner ring of "white matter" separated from the outer
"gray matter". Return the mesh, cell tags (gray = 1, white = 2) and facet tags
(pial = 1, ventricle = 2) via dolfinx.io.gmsh.model_to_mesh. Follow the facet-tag
conventions documented in mesh.py. Test that the areas of the two subdomains match
the analytical ellipse areas to within a mesh-dependent tolerance.
```

### 3.2 Estimating the diffusion coefficient from data (inverse problem)

```text
A common research question is: what effective diffusion coefficient best explains
the tracer concentrations measured in MRI? Add `biodiff/inverse.py` with
`estimate_diffusion(geometry, observations, observation_times, ...)`, which fits D
(and optionally the clearance k) by minimising the squared misfit between simulated
and observed ROI means, using scipy.optimize. First generate synthetic observations
with a known D, add 1% noise with a fixed seed, and check that the estimate recovers
D to within 5%. Plan this first and tell me which optimiser you'd choose and why.
```

### 3.3 Oxygen in tumour tissue (non-linear reaction)

```text
Oxygen consumption in tissue follows Michaelis–Menten kinetics:
-div(D grad c) = -V_max * c / (K_m + c). Add a `SteadyNonlinearSolver` that solves
this with dolfinx.fem.petsc.NonlinearProblem and Newton's method. Use literature
values for D, V_max and K_m (in mm and s), and cite your sources in docstrings. Add an
example of a 2D tissue slab with oxygen supplied from a blood vessel on one side, and
compute the hypoxic fraction (the area where c < threshold). Test that as K_m
becomes very large the problem reduces to linear decay with k = V_max / K_m, and that
the solution stays non-negative.
```

### 3.4 Two-compartment model (blood and tissue)

```text
Implement a two-compartment model in which tracer moves between the extracellular
space (concentration u_e) and the blood or perivascular space (u_b):
  phi_e du_e/dt - div(D_e grad u_e) = -beta (u_e - u_b)
  phi_b du_b/dt - div(D_b grad u_b) =  beta (u_e - u_b) - k_b u_b
Solve it as a block (mixed) system with backward Euler. Test that with k_b = 0 and
no-flux boundaries, the combined amount phi_e*u_e + phi_b*u_b is conserved, and that
with beta = 0 the compartments evolve independently. Update the README with the
model and its parameters.
```

### 3.5 Glymphatic transport: diffusion plus convection

```text
Add an optional velocity field `w` to DiffusionSolver, which adds the term
div(w u) to model convection-enhanced or glymphatic transport. Add SUPG
stabilisation that can be switched on for high Péclet numbers. Write a
convergence test using the method of manufactured solutions that checks
second-order L2 convergence in space for P1 elements, and report the observed
convergence rates.
```

### 3.6 Uncertainty quantification

```text
Tissue parameters are uncertain. Add `biodiff/uq.py` with a Monte Carlo driver that
samples D and k from log-normal distributions, runs the simulation for each sample,
and returns the mean and 5–95% percentile bands of a chosen quantity of interest over
time. The runs should be reproducible with a seed. Make a matplotlib plot in an
example script. Test that with zero variance, every sample equals the deterministic
solution.
```

---

## Level 4: Software engineering prompts

```text
Set up a GitHub Actions workflow that runs ruff and pytest (serial and with
mpirun -n 2) inside the ghcr.io/fenics/dolfinx/dolfinx:stable container.
```

```text
Add a pre-commit configuration with ruff (lint + format) and basic hygiene hooks.
```

```text
Add a Sphinx (or Jupyter Book) documentation site that renders the README, the API
reference from docstrings, and one tutorial notebook using the quick-start example.
```

```text
Review the package for performance. In particular, check that forms are compiled
only once and that no matrices are reassembled unnecessarily inside the time loop.
Propose changes with before/after timings on a 3D box with n=32.
```
