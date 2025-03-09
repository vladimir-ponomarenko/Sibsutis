import numpy as np
import matplotlib.pyplot as plt
from scipy.fft import fft, fftfreq

N = 100 
L = 2 
pulse_width = 0.5
x = np.linspace(-L / 2, L / 2, N, endpoint=False)

# --- Прямоугольный сигнал по середине от 0 ---
rect_signal = np.where(np.abs(x) <= pulse_width / 2, 1, 0)

rect_signal_fft = fft(rect_signal)
frequencies = fftfreq(N, L / N)

plt.figure(figsize=(12, 6))
plt.subplot(2, 3, 1)
plt.plot(x, rect_signal)
plt.title("Прямоугольный сигнал")
plt.xlabel("Время")
plt.ylabel("Амплитуда")
plt.grid(True)

plt.subplot(2, 3, 4)
plt.stem(frequencies, np.abs(rect_signal_fft))
plt.title("Амплитудный спектр")
plt.xlabel("Частота")
plt.ylabel("Амплитуда")
plt.grid(True)
plt.xlim(-5, 5)

# --- Изменение длительности импульса ---
new_pulse_width = pulse_width * 2.5 
rect_signal2 = np.where(np.abs(x) <= new_pulse_width / 2, 1, 0)

# --- Амплитудный спектр ---
rect_signal_fft2 = fft(rect_signal2)
frequencies2 = fftfreq(N, L / N)

plt.subplot(2, 3, 2)
plt.plot(x, rect_signal2)
plt.title("Измененная длительность импульса x2.5")
plt.xlabel("Время")
plt.ylabel("Амплитуда")
plt.grid(True)

plt.subplot(2, 3, 5)
plt.stem(frequencies2, np.abs(rect_signal_fft2))
plt.title("Амплитудный спектр")
plt.xlabel("Частота")
plt.ylabel("Амплитуда")
plt.grid(True)
plt.xlim(-5, 5)

# --- Вынесение сигнала из отрицательной области ---
x3 = np.linspace(0, L, N, endpoint=False)
rect_signal3 = np.where((x3 >= pulse_width / 2) & (x3 <= pulse_width / 2 + pulse_width), 1, 0)

rect_signal_fft3 = fft(rect_signal3)
frequencies3 = fftfreq(N, L / N)

plt.subplot(2, 3, 3)
plt.plot(x3, rect_signal3)
plt.title("Вынесение из отрицат. обл.")
plt.xlabel("Время")
plt.ylabel("Амплитуда")
plt.grid(True)

plt.subplot(2, 3, 6)
plt.stem(frequencies3, np.abs(rect_signal_fft3))
plt.title("Амплитудный спектр")
plt.xlabel("Частота")
plt.ylabel("Амплитуда")
plt.grid(True)
plt.xlim(-5, 5)

plt.tight_layout()
plt.show()
