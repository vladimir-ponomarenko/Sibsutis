import numpy as np
from scipy import signal
import matplotlib.pyplot as plt

f = 5
T = 1 / f
Ts = 0.01
f0 = 5
phi = 0
A = 2 

# t = np.linspace(-0.1, 0.1, 100, endpoint=False)
t = np.arange(-0.1, 0.1, Ts)
s = 2 * np.cos(2 * np.pi * f * t)
sc = np.cos(2 * np.pi * f * t)
ss = np.sin(2 * np.pi * f * t)

x = A * np.cos(2 * np.pi * f0 * t + phi)

n_values = np.arange(0, 5) 
an = np.zeros(len(n_values))
bn = np.zeros(len(n_values))

for i, n in enumerate(n_values):
    an[i] = (1 / T) * np.trapz(x * np.cos(n * 2 * np.pi * t / T), t)
    bn[i] = (2 / T) * np.trapz(x * np.sin(n * 2 * np.pi * t / T), t)


An = np.sqrt(an**2 + bn**2)
phin = np.arctan2(bn, an)

print("Коэффициенты an:", an)
print("Коэффициенты bn:", bn)
print("Амплитуды An:", An)
print("Фазы phin (рад):", phin)

m1 = s * sc
m2 = s * ss

# plt.plot(t, s, t, sc, t, m1)
# plt.ylim(-2, 2)

a1 = (1 / T) * np.sum(m1) * Ts  