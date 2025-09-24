import numpy as np
import matplotlib.pyplot as plt

fc = 2e9          # частота несущей (Гц)
c = 3e8           # скорость света (м/с)
lam = c / fc      # длина волны
F = 16
V = 10            # скорость абонента (м/с)
D = 1000          # расстояние до БС (м)
N = 100           # число точек
NFFT = 128
alpha = np.pi/6   # угол движения (30°)  

dx = lam / F
n = np.arange(N)
t = n * dx / V              
fs = 1 / (dx / V)           

MSx = V * t * np.cos(alpha)
MSy = V * t * np.sin(alpha)

BSx, BSy = D, 0

dist = np.sqrt((BSx - MSx)**2 + (BSy - MSy)**2)

k = 2 * np.pi / lam
r = np.exp(-1j * k * dist)

R = np.fft.fftshift(np.fft.fft(r, NFFT))
freq = np.fft.fftshift(np.fft.fftfreq(NFFT, d=1/fs))

doppler_idx = np.argmax(np.abs(R))
doppler_shift = freq[doppler_idx]

amplitude = np.abs(r)
phase = np.angle(r)

print(f"Макс. амплитуда: {np.max(amplitude):.3f}")
print(f"Фаза (первые 5 точек): {phase[:5]}")
print(f"Смещение Допплера: {doppler_shift:.2f} Гц")

plt.figure(figsize=(10, 7))

plt.subplot(3, 1, 1)
plt.plot(t, amplitude, 'b', linewidth=1.5)
plt.title("Амплитуда", fontsize=12)
plt.xlabel("Время, с")
plt.ylabel("|r(t)|")
plt.grid(True)

plt.subplot(3, 1, 2)
plt.plot(t, phase, 'g', linewidth=1.5)
plt.title("Фаза", fontsize=12)
plt.xlabel("Время, с")
plt.ylabel("∠r(t), рад")
plt.grid(True)

plt.subplot(3, 1, 3)
plt.plot(freq, np.abs(R), 'r', linewidth=1.5)
plt.title("Спектр (Допплер)", fontsize=12)
plt.xlabel("Частота, Гц")
plt.ylabel("|R(f)|")
plt.grid(True)

plt.tight_layout()
plt.show()