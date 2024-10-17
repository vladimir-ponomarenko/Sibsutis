from scipy.integrate import simpson
import matplotlib.pyplot as plt
import numpy as np

# Два прямоугольных сигнала
t = np.linspace(-10, 10, 1000)

rect1 = np.where(np.abs(t) <= 1, 1, 0)

rect2 = np.where(np.abs(t) <= 1, 1, 0)

dt = t[1] - t[0]

manual_convolution = np.zeros_like(t)

# y(t) = интеграл x(τ) * h(t - τ) dτ
for i in range(len(t)):
    tau = t[i] - t 
    h_shifted = np.where(np.abs(tau) <= 1, 1, 0) 
    manual_convolution[i] = simpson(rect1 * h_shifted)

plt.figure(figsize=(12, 6))

plt.subplot(3, 1, 1)
plt.plot(t, rect1, label='Rect1')
plt.title('Первый прямоугольный сигнал')
plt.grid(True)

plt.subplot(3, 1, 2)
plt.plot(t, rect2, label='Rect2')
plt.title('Второй прямоугольный сигнал')
plt.grid(True)

plt.subplot(3, 1, 3)
plt.plot(t, manual_convolution, label='Свертка')
plt.title('Свертка прямоугольных сигналов')
plt.grid(True)

plt.tight_layout()
plt.show()
