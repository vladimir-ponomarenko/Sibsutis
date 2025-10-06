import numpy as np
import matplotlib.pyplot as plt
from scipy import signal

sigma = 1.0
N = 8000
fs = 120
hi = np.random.normal(0, sigma, N)
hq = np.random.normal(0, sigma, N)
h = hi + 1j * hq

filter_order = 5
cutoff_norm = 0.1
b, a = signal.butter(filter_order, cutoff_norm, btype='low')
h_filtered = signal.lfilter(b, a, h)
acf_orig_raw = np.correlate(h, h, mode='full')
acf_orig_normalized = np.abs(acf_orig_raw) / np.max(np.abs(acf_orig_raw))
acf_filtered_raw = np.correlate(h_filtered, h_filtered, mode='full')
acf_filtered_normalized = np.abs(acf_filtered_raw) / np.max(np.abs(acf_filtered_raw))

lags = np.arange(-N + 1, N)
lags_sec = lags / fs


plt.figure(figsize=(15, 8))

plt.subplot(2, 3, 1)
plt.hist(np.abs(h), bins=80, density=True, color='gray')
plt.title('|h| до фильтрации (Рэлей)')
plt.xlabel('Амплитуда')
plt.ylabel('Плотность вероятности')

plt.subplot(2, 3, 2)
plt.hist(np.angle(h), bins=80, density=True, color='gray')
plt.title('arg(h) до фильтрации (Равномерное)')
plt.xlabel('Фаза, рад')

plt.subplot(2, 3, 3)
plt.plot(lags_sec, acf_orig_normalized, color='gray')
plt.title('Нормированная АКФ до фильтрации')
plt.xlabel('Лаг, с')
plt.ylabel('Норм. |ACF|')
plt.xlim(-0.5, 0.5)
plt.ylim(0, 1.1)#W

plt.subplot(2, 3, 4)
plt.hist(np.abs(h_filtered), bins=80, density=True, color='blue')
plt.title('|h| после фильтрации (Рэлей)')
plt.xlabel('Амплитуда')
plt.ylabel('Плотность вероятности')

plt.subplot(2, 3, 5)
plt.hist(np.angle(h_filtered), bins=80, density=True, color='blue')
plt.title('arg(h) после фильтрации (Равномерное)')
plt.xlabel('Фаза, рад')

plt.subplot(2, 3, 6)
plt.plot(lags_sec, acf_filtered_normalized, color='blue')
plt.title('Нормированная АКФ после фильтрации')
plt.xlabel('Лаг, с')
plt.ylabel('Норм. |ACF|')
plt.xlim(-0.5, 0.5)
plt.ylim(0, 1.1)

plt.suptitle('Сравнение характеристик сигнала до и после фильтрации', fontsize=16)
plt.tight_layout(rect=[0, 0, 1, 0.96])
plt.show()