import numpy as np
from scipy import signal
import matplotlib.pyplot as plt

f = 5
T = 1 / f
Ts = 0.01
f0 = 5
phi = 0
A = 2

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

print("Фаза = 0")
print("Коэффициенты an:", an)
print("Коэффициенты bn:", bn)
print("Амплитуды An:", An)
print("Фазы phin (рад):", phin)

plt.figure(figsize=(12, 9))

plt.subplot(3, 2, 1)
plt.plot(phin, An, 'o-') 
plt.xlabel('phin (рад)')
plt.ylabel('An')
plt.title('An от phin (Фаза = 0)')

plt.subplot(3, 2, 2)
plt.stem(n_values, An)
plt.title('An от n (Фаза = 0)')

plt.subplot(3, 2, 3)
plt.stem(n_values, phin)
plt.title('phin(n) (Фаза = 0)')

phi = np.pi / 4
x = A * np.cos(2 * np.pi * f0 * t + phi)

for i, n in enumerate(n_values):
    an[i] = (1 / T) * np.trapz(x * np.cos(n * 2 * np.pi * t / T), t)
    bn[i] = (2 / T) * np.trapz(x * np.sin(n * 2 * np.pi * t / T), t)

An = np.sqrt(an**2 + bn**2)
phin = np.arctan2(bn, an)

print("\nФаза = pi/4")
print("Коэффициенты an:", an)
print("Коэффициенты bn:", bn)
print("Амплитуды An:", An)
print("Фазы phin (рад):", phin)

plt.subplot(3, 2, 4)
plt.plot(phin, An, 'o-')
plt.xlabel('phin (рад) (сдвиг фазы)')
plt.ylabel('An')
plt.title('An от phin (Фаза = pi/4)')

plt.subplot(3, 2, 5)
plt.stem(n_values, An)
plt.title('An от n (Фаза = pi/4)')

plt.subplot(3, 2, 6)
plt.stem(n_values, phin)
plt.title('phin(n) (Фаза = pi/4)')


plt.tight_layout()
plt.show()