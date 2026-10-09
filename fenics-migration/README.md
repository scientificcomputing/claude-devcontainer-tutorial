# fenics-migration

An environment for translating legacy FEniCS code into FEniCSx. Two containers run
side by side, defined in [.devcontainer/compose.yaml](.devcontainer/compose.yaml):

| Service | Image | Use |
| --- | --- | --- |
| `fenicsx` | `ghcr.io/fenics/dolfinx/dolfinx:stable` | VS Code and Claude Code run here |
| `legacy` | `ghcr.io/scientificcomputing/fenics-gmsh:2024-05-13` | Legacy FEniCS (dolfin 2019.2) with gmsh |

Both containers mount this folder at `/home/shared`. From the `fenicsx` container you
run code in the legacy one with the `legacy` command:

```bash
python3 fenicsx/poisson.py           # FEniCSx
legacy python3 legacy/poisson.py     # legacy FEniCS
legacy mpirun -n 2 python3 legacy/poisson.py
legacy                               # shell in the legacy container
```

`legacy` ([.devcontainer/legacy](.devcontainer/legacy)) is a thin wrapper around
`docker exec`. It works because the dev container has the Docker CLI (from the
`docker-outside-of-docker` feature), which talks to the host's Docker. That means
code in the dev container can control Docker on your machine. That's fine for this
tutorial, but keep it in mind.

The legacy image is built only for amd64. On Apple Silicon it runs under emulation,
which works but is slower. Enable "Use Rosetta for x86/amd64 emulation" in Docker
Desktop (or the equivalent setting in OrbStack/Colima) to speed it up.

[CLAUDE.md](CLAUDE.md) tells Claude about this setup, so it knows to use `legacy`.

## Layout

| Folder | Contents |
| --- | --- |
| [legacy/](legacy/) | The legacy FEniCS code to translate (a Poisson demo to start with) |
| [fenicsx/](fenicsx/) | Where the translated DOLFINx code goes (empty) |

## Example prompt

```text
Translate legacy/poisson.py to DOLFINx and save it as fenicsx/poisson.py. Run both
versions and check that the printed L2 norms agree to at least 1e-6. Write the
solution to results/poisson_fenicsx.bp with VTXWriter. Explain the main API
changes you had to make.
```
