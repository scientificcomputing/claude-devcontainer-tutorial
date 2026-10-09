# multiple-fenicsx-setup

Shows how to define more than one dev container for the same project. Here the same
code runs against two DOLFINx versions:

| Config | Image |
| --- | --- |
| [.devcontainer/stable](.devcontainer/stable/devcontainer.json) | `ghcr.io/fenics/dolfinx/dolfinx:stable` |
| [.devcontainer/nightly](.devcontainer/nightly/devcontainer.json) | `ghcr.io/fenics/dolfinx/dolfinx:nightly` |

When you run **Dev Containers: Reopen in Container**, VS Code asks which config to use.
To switch later, run **Dev Containers: Switch Container**.

The package `fenicsx_demo` is a placeholder, so `pip install -e .[dev]` in
[.devcontainer/setup.sh](.devcontainer/setup.sh) has something to install. Replace it
with your own code.

## Running the tests

```bash
python3 -m pytest
mpirun -n 2 python3 -m pytest   # in parallel
```
