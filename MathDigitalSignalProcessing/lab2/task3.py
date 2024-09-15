import numpy as np
import matplotlib.pyplot as plt

f0 = 1
t = np.linspace(0, 2, 200)

A1 = 2
phi1 = np.pi / 4
A2 = 1
phi2 = 3 * np.pi / 4

x1 = A1 * np.cos(2 * np.pi * f0 * t + phi1)
x2 = A2 * np.cos(2 * np.pi * f0 * t + phi2)
x_sum_2 = x1 + x2

A_sum_2 = np.max(x_sum_2)
first_max_idx = np.argmax(x_sum_2)
t_phi_2 = t[first_max_idx]
phi_sum_2 = -2 * np.pi * f0 * t_phi_2 / np.pi 

plt.figure(figsize=(10, 4))
plt.plot(t, x1)
plt.plot(t, x2)
plt.plot(t, x_sum_2)
plt.title("Сложение двух гармонических колебаний")
plt.xlabel("Время (с)")
plt.ylabel("Амплитуда")
plt.grid(True)
plt.show()

A3 = 1.5
phi3 = np.pi / 2

x3 = A3 * np.cos(2 * np.pi * f0 * t + phi3)
x_sum_3 = x1 + x2 + x3

A_sum_3 = np.max(x_sum_3)
first_max_idx = np.argmax(x_sum_3)
t_phi_3 = t[first_max_idx]
phi_sum_3 = -2 * np.pi * f0 * t_phi_3 / np.pi

plt.figure(figsize=(10, 4))
plt.plot(t, x1)
plt.plot(t, x2)
plt.plot(t, x3)
plt.plot(t, x_sum_3)
plt.title("Сложение трех гармонических колебаний")
plt.xlabel("Время (с)")
plt.ylabel("Амплитуда")
plt.grid(True)
plt.show()

print(f"Для суммы двух колебаний: A = {A_sum_2:.2f}, phi = {phi_sum_2:.2f}π")
print(f"Для суммы трех колебаний: A = {A_sum_3:.2f}, phi = {phi_sum_3:.2f}π")
