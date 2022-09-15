import numpy as np

a = 1.00005
b = 1.00002
print(np.isclose(a,b,rtol=2e-5,atol=5e-6))