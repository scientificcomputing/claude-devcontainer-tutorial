# CLAUDE.md

This project is for translating legacy FEniCS (dolfin) code into FEniCSx (DOLFINx).

## Environment

You are running in a dev container with DOLFINx (stable). A second container with
legacy FEniCS (dolfin 2019.2) runs alongside it and shares the workspace at
`/home/shared`.

- Run FEniCSx code directly: `python3 fenicsx/poisson.py`
- Run legacy code with the `legacy` prefix: `legacy python3 legacy/poisson.py`
  (also `legacy mpirun -n 2 python3 ...`). Run it from inside `/home/shared`.

`import dolfin` only works through `legacy`. `import dolfinx` only works without it.

## Layout

- `legacy/` - original legacy FEniCS code. Don't modify it; it's the reference.
- `fenicsx/` - translated DOLFINx code, one file per legacy file with the same name.

## Translating

- When translating, run both versions and compare a quantity printed by both
  (for example an L2 norm) to confirm the translation matches.
- Legacy `UnitSquareMesh` uses "right" diagonals. Use
  `diagonal=mesh.DiagonalType.right` in DOLFINx to get the same mesh.
- The legacy container is amd64-only and may run under emulation, so it can be slow.
