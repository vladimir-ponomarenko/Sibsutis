import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import freqz

fs = 500
t = np.arange(0, 1, 1/fs)
f1 = 5
f2 = 50

signal = 0.5 * np.sin(2 * np.pi * f1 * t) + 0.3 * np.sin(2 * np.pi * f2 * t)

filter_length = 64
n = np.arange(0, filter_length)

def create_filter(window_type, filter_length):
    if window_type == 'hamming':
        window = np.hamming(filter_length)
    elif window_type == 'bartlett':
        window = np.bartlett(filter_length)
    elif window_type == 'hanning':
        window = np.hanning(filter_length)
    else:
        raise ValueError("Неизвестный тип окна.")
    
    h = np.sinc(2 * (n - filter_length/2) / fs)
    
    h_windowed = h * window
    return h_windowed / np.sum(h_windowed)

hamming_filter = create_filter('hamming', filter_length)
bartlett_filter = create_filter('bartlett', filter_length)
hanning_filter = create_filter('hanning', filter_length)

w, h_no_window = freqz(np.sinc(np.arange(0, filter_length) - filter_length // 2), 1, worN=512)
w_hamming, h_hamming = freqz(hamming_filter, 1, worN=512)
w_bartlett, h_bartlett = freqz(bartlett_filter, 1, worN=512)
w_hanning, h_hanning = freqz(hanning_filter, 1, worN=512)

filtered_signal_hamming = np.convolve(signal, hamming_filter, mode='same')
filtered_signal_bartlett = np.convolve(signal, bartlett_filter, mode='same')
filtered_signal_hanning = np.convolve(signal, hanning_filter, mode='same')

def compute_spectrum(signal):
    freq = np.fft.fftfreq(len(signal), 1/fs)
    spectrum = np.fft.fft(signal)
    return freq, np.abs(spectrum)

freq_orig, spectrum_orig = compute_spectrum(signal)
freq_hamming, spectrum_hamming = compute_spectrum(filtered_signal_hamming)
freq_bartlett, spectrum_bartlett = compute_spectrum(filtered_signal_bartlett)
freq_hanning, spectrum_hanning = compute_spectrum(filtered_signal_hanning)

plt.figure(figsize=(15, 15))

plt.subplot(4, 1, 1)
plt.plot(w / np.pi * fs / 2, 20 * np.log10(np.abs(h_no_window)), label='Без окна', color='gray')
plt.plot(w_hamming / np.pi * fs / 2, 20 * np.log10(np.abs(h_hamming)), label='Hamming', color='blue')
plt.plot(w_bartlett / np.pi * fs / 2, 20 * np.log10(np.abs(h_bartlett)), label='Bartlett', color='green')
plt.plot(w_hanning / np.pi * fs / 2, 20 * np.log10(np.abs(h_hanning)), label='Hanning', color='red')
plt.title('Частотные характеристики фильтров')
plt.xlabel('Частота (Гц)')
plt.ylabel('Амплитуда (дБ)')
plt.grid()
plt.legend()

plt.subplot(4, 1, 2)
plt.plot(t, signal, label='Исходный сигнал', color='black', alpha=0.5)
plt.plot(t, filtered_signal_hamming, label='Отфильтрованный Hamming', color='blue', linestyle='--')
plt.plot(t, filtered_signal_bartlett, label='Отфильтрованный Bartlett', color='green', linestyle='--')
plt.plot(t, filtered_signal_hanning, label='Отфильтрованный Hanning', color='red', linestyle='--')
plt.title('Сигналы до и после фильтрации')
plt.xlabel('Время (с)')
plt.ylabel('Амплитуда')
plt.grid()
plt.legend()

plt.subplot(4, 1, 3)
plt.plot(np.hanning(filter_length), label='Hanning', color='red')
plt.plot(np.hamming(filter_length), label='Hamming', color='blue')
plt.plot(np.bartlett(filter_length), label='Bartlett', color='green')
plt.title('Весовые окна')
plt.xlabel('Отсчет')
plt.ylabel('Амплитуда')
plt.grid()
plt.legend()

plt.subplot(4, 1, 4)
plt.plot(freq_orig, spectrum_orig, label='Спектр исходного сигнала', color='black')
plt.plot(freq_hamming, spectrum_hamming, label='Спектр Hamming', color='blue', linestyle='--')
plt.plot(freq_bartlett, spectrum_bartlett, label='Спектр Bartlett', color='green', linestyle='--')
plt.plot(freq_hanning, spectrum_hanning, label='Спектр Hanning', color='red', linestyle='--')
plt.title('Спектры сигналов до и после фильтрации')
plt.xlabel('Частота (Гц)')
plt.ylabel('Амплитуда')
plt.grid()
plt.legend()

plt.tight_layout()
plt.show()
