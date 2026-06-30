import sympy as sp
x, y, z = sp.symbols('x y z')
f = 2*x + sp.sinh(sp.exp(5*x)) - 6*y + 9*sp.cos(sp.atan(z))
grad_f = [sp.diff(f, var) for var in (x, y, z)]
direction_vector = sp.Matrix([0, 0, 1])
result = sum(grad_f[i] * direction_vector[i] for i in range(3))
print(result)