# spack-env

A dev container for working with [Spack](https://spack.io). The image is built from
[.devcontainer/Dockerfile](.devcontainer/Dockerfile), which installs Spack's
prerequisites and clones Spack into `/opt/spack`.

When the container is created it runs

```bash
spack compiler find
spack repo add spack_repo/scientificcomputing
```

which registers the local package repository in
[spack_repo/scientificcomputing](spack_repo/scientificcomputing). The repository is
empty. Add packages under `packages/<name>/package.py`, or ask Claude to write one:

```text
Create a Spack package for <project> in spack_repo/scientificcomputing, then
check that it works with `spack info` and `spack install`.
```
