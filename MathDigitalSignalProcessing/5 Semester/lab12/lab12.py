import numpy as np
import matplotlib.pyplot as plt
from scipy.fft import fft, fftfreq
from scipy.signal import freqz, lfilter

f1 = 5000
fs = 14400

wc = 2 * np.pi * f1 / fs

M_values = [3, 7]

t = np.arange(0, 0.01, 1/fs)
signal_in = np.sin(2*np.pi*1000*t) + np.sin(2*np.pi*6000*t)



for M in M_values:
    n = np.arange(-M, M + 1)
    h = np.sin(wc * n) / (np.pi * n)
    h[M] = wc / np.pi

    signal_out = lfilter(h, 1.0, signal_in)

    freqs_in = fftfreq(len(signal_in), 1/fs)
    spectrum_in = np.abs(fft(signal_in))

    freqs_out = fftfreq(len(signal_out), 1/fs)
    spectrum_out = np.abs(fft(signal_out))


    plt.figure(figsize=(12, 8))

    plt.subplot(3, 2, 1)
    plt.stem(n, h)
    plt.title(f'Импульсная характеристика (M = {M})')


    w, hf = freqz(h, worN=8000)
    f = w * fs / (2 * np.pi)
    plt.subplot(3, 2, 2)
    plt.plot(f, 20 * np.log10(np.abs(hf)))
    plt.title(f'АЧХ (M = {M})')
    plt.xlim(0, fs/2)


    plt.subplot(3, 2, 3)
    plt.plot(freqs_in, spectrum_in)
    plt.title('Спектр входного сигнала')
    plt.xlim(0, fs/2)


    plt.subplot(3, 2, 4)
    plt.plot(freqs_out, spectrum_out)
    plt.title('Спектр выходного сигнала')
    plt.xlim(0, fs/2)
    

    plt.subplot(3, 2, 5)
    plt.plot(f, np.angle(hf))
    plt.title(f'ФЧХ (M = {M})')
    plt.xlim(0, fs/2) 

    plt.tight_layout()
    plt.show()

    print(f"Коэффициенты ИХ для M = {M}: {h}")
