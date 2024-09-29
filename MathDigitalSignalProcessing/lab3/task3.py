import numpy as np
import matplotlib.pyplot as plt

T = 2  
tau = 1  

Ts = 0.01
t = np.arange(-T/2, T/2, Ts)

x = np.zeros_like(t)
x[(t >= -tau/2) & (t < tau/2)] = 1

n_values = np.arange(-5, 6) 
an = np.zeros(len(n_values))
bn = np.zeros(len(n_values))

for i, n in enumerate(n_values):
    an[i] = (2 / T) * np.trapz(x * np.cos(n * 2 * np.pi * t / T), t)
    bn[i] = (2 / T) * np.trapz(x * np.sin(n * 2 * np.pi * t / T), t)

An = np.sqrt(an**2 + bn**2)
phin = np.arctan2(bn, an)

print("Коэффициенты an:", an)
print("Коэффициенты bn:", bn)
print("Амплитуды An:", An)
print("Фазы phin (рад):", phin)

plt.figure(figsize=(12, 9))

plt.subplot(3, 2, 1)
plt.plot(t, x)
plt.title("Прямоугольный сигнал")
plt.xlabel("Время (с)")
plt.ylabel("Амплитуда")

plt.subplot(3, 2, 2)
plt.stem(n_values, an)
plt.title("Коэффициенты an")
plt.xlabel("n")
plt.ylabel("Амплитуда")

plt.subplot(3, 2, 3)
plt.stem(n_values, bn)
plt.title("Коэффициенты bn")
plt.xlabel("n")
plt.ylabel("Амплитуда")

plt.subplot(3, 2, 4)
plt.plot(phin, An, 'o-')
plt.xlabel('phin (рад)')
plt.ylabel('An')
plt.title('An от phin')

plt.subplot(3, 2, 5)
plt.stem(n_values, An)
plt.title('An от n')
plt.xlabel("n")
plt.ylabel("Амплитуда")

plt.subplot(3, 2, 6)
plt.stem(n_values, phin)
plt.title('phin(n)')
plt.xlabel("n")
plt.ylabel("Фаза (рад)")

plt.tight_layout()
plt.show()