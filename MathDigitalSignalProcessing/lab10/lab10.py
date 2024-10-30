import numpy as np
import matplotlib.pyplot as plt

x = np.array([1, 2, 3, 0.5])

N = 12

n_h = np.arange(4)
h = np.exp(-0.1 * N * n_h)

y = np.convolve(x, h)

y0 = x[0] * h[0]
y1 = x[0] * h[1] + x[1] * h[0]
y2 = x[0] * h[2] + x[1] * h[1] + x[2] * h[0]
y3 = x[0] * h[3] + x[1] * h[2] + x[2] * h[1] + x[3] * h[0]
y4 = x[1] * h[3] + x[2] * h[2] + x[3] * h[1]
y5 = x[2] * h[3] + x[3] * h[2]
y6 = x[3] * h[3]

plt.figure(figsize=(10, 6))

plt.subplot(3, 1, 1)
plt.stem(np.arange(len(x)), x)
plt.title('Входной сигнал x(n)')
plt.xlabel('n')
plt.ylabel('x(n)')
plt.grid(True)

plt.subplot(3, 1, 2)
plt.stem(np.arange(len(h)), h)
plt.title('Импульсная характеристика h(n)')
plt.xlabel('n')
plt.ylabel('h(n)')
plt.grid(True)

plt.subplot(3, 1, 3)
plt.stem(np.arange(len(y)), y)
plt.title('Результат свертки y(n)')
plt.xlabel('n')
plt.ylabel('y(n)')
plt.grid(True)

print("Ручной расчет:")
print(f"y(0) = {y0}")
print(f"y(1) = {y1}")
print(f"y(2) = {y2}")
print(f"y(3) = {y3}")
print(f"y(4) = {y4}")
print(f"y(5) = {y5}")
print(f"y(6) = {y6}")

print("\nРезультат свертки (np.convolve):", y)

plt.tight_layout()
plt.show()
