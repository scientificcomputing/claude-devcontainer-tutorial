"""Poisson equation in legacy FEniCS (dolfin), adapted from the classic demo.

-div(grad(u)) = f    in the unit square
            u = 0    on x = 0 and x = 1
        du/dn = g    on y = 0 and y = 1
"""

from dolfin import *

mesh = UnitSquareMesh(32, 32)
V = FunctionSpace(mesh, "Lagrange", 1)


def boundary(x):
    return x[0] < DOLFIN_EPS or x[0] > 1.0 - DOLFIN_EPS


bc = DirichletBC(V, Constant(0.0), boundary)

u = TrialFunction(V)
v = TestFunction(V)
f = Expression("10*exp(-(pow(x[0] - 0.5, 2) + pow(x[1] - 0.5, 2)) / 0.02)", degree=2)
g = Expression("sin(5*x[0])", degree=2)
a = inner(grad(u), grad(v)) * dx
L = f * v * dx + g * v * ds

u = Function(V)
solve(a == L, u, bc)

print(f"L2 norm of u: {norm(u, 'L2'):.8f}")

with XDMFFile(mesh.mpi_comm(), "results/poisson_legacy.xdmf") as xdmf:
    xdmf.write(u)
