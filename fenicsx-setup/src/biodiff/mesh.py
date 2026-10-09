"""Simple meshes with tagged boundaries.

Boundary facets are tagged with integer markers so that boundary conditions
can be applied to individual sides of the domain:

    1: x = x_min, 2: x = x_max, 3: y = y_min, 4: y = y_max, 5: z = z_min, 6: z = z_max
"""

from typing import NamedTuple

import dolfinx
import numpy as np
from mpi4py import MPI


class Geometry(NamedTuple):
    mesh: dolfinx.mesh.Mesh
    facet_tags: dolfinx.mesh.MeshTags


def _tag_box_boundaries(
    mesh: dolfinx.mesh.Mesh,
    lower: np.ndarray,
    upper: np.ndarray,
) -> dolfinx.mesh.MeshTags:
    tdim = mesh.topology.dim
    fdim = tdim - 1
    mesh.topology.create_connectivity(fdim, tdim)

    indices: list[np.ndarray] = []
    values: list[np.ndarray] = []
    for axis in range(tdim):
        for side, coord in enumerate((lower[axis], upper[axis])):
            facets = dolfinx.mesh.locate_entities_boundary(
                mesh,
                fdim,
                lambda x, a=axis, c=coord: np.isclose(x[a], c),
            )
            indices.append(facets)
            values.append(np.full_like(facets, 2 * axis + side + 1))

    all_indices = np.hstack(indices).astype(np.int32)
    all_values = np.hstack(values).astype(np.int32)
    # Facets on edges/corners belong to several sides; keep one tag per facet.
    unique_indices, first = np.unique(all_indices, return_index=True)
    return dolfinx.mesh.meshtags(mesh, fdim, unique_indices, all_values[first])


def rectangle_mesh(
    length: float = 1.0,
    height: float = 1.0,
    n: int = 16,
    comm: MPI.Comm = MPI.COMM_WORLD,
) -> Geometry:
    """Create a triangulated rectangle [0, length] x [0, height] with tagged sides."""
    lower = np.array([0.0, 0.0])
    upper = np.array([length, height])
    mesh = dolfinx.mesh.create_rectangle(
        comm,
        [lower, upper],
        [n, n],
        cell_type=dolfinx.mesh.CellType.triangle,
    )
    return Geometry(mesh, _tag_box_boundaries(mesh, lower, upper))


def box_mesh(
    length: float = 1.0,
    width: float = 1.0,
    height: float = 1.0,
    n: int = 8,
    comm: MPI.Comm = MPI.COMM_WORLD,
) -> Geometry:
    """Create a tetrahedral box [0, length] x [0, width] x [0, height] with tagged sides."""
    lower = np.array([0.0, 0.0, 0.0])
    upper = np.array([length, width, height])
    mesh = dolfinx.mesh.create_box(
        comm,
        [lower, upper],
        [n, n, n],
        cell_type=dolfinx.mesh.CellType.tetrahedron,
    )
    return Geometry(mesh, _tag_box_boundaries(mesh, lower, upper))
