import numpy as np
import scipy.signal as sig
import matplotlib.pyplot as plt

fs = 30000  
N = 1000    
f_c = 5000  
omega = 2 * np.pi * f_c  

t = np.arange(N) / fs

noise = np.random.normal(0, 1, N)

b = [1]
a = [1, -0.9]

x_c = sig.lfilter(b, a, noise)
x_s = x_c.copy()  

part1 = x_c * 2 * np.cos(2 * omega * t)
part2 = x_s * 2 * np.sin(2 * omega * t)

y = part1 + part2

chnl = np.array([
    0.112873323983817 + 0.707197839105975j,
    0.447066470535225 - 0.375487664593309j,
    0.189507622364489 - 0.132430466488543j,
    0.111178811342494 - 0.0857241111225552j
])

y_channel = np.convolve(y, chnl, mode='same')

y_cos = y_channel * 2 * np.cos(2 * omega * t)
y_sin = y_channel * 2 * np.sin(2 * omega * t)

Xc = sig.lfilter(b, a, y_cos)
Xs = sig.lfilter(b, a, y_sin)

A = np.sqrt(Xc**2 + Xs**2)

def autocorr(x):
    x = x - np.mean(x)
    result = np.correlate(x, x, mode='full')
    return result[len(x)-1:]

acf_y = autocorr(y)

f_y, Pxx_y = sig.welch(y, fs, nperseg=512)

def crosscorr(x, y):
    x = x - np.mean(x)
    y = y - np.mean(y)
    return np.correlate(x, y, mode='full')

ccf = crosscorr(y, y_channel)

plt.figure(figsize=(12, 16))

plt.subplot(6, 1, 1)
plt.plot(t, part1)
plt.title('part1: x_c * 2cos(2ωt)')
plt.xlabel('Время (с)')
plt.ylabel('Амплитуда')
plt.grid()

plt.subplot(6, 1, 2)
plt.plot(t, part2)
plt.title('part2: x_s * 2sin(2ωt)')
plt.xlabel('Время (с)')
plt.ylabel('Амплитуда')
plt.grid()

plt.subplot(6, 1, 3)
plt.plot(t, y)
plt.title('Узкополосный процесс y(t)')
plt.xlabel('Время (с)')
plt.ylabel('Амплитуда')
plt.grid()

plt.subplot(6, 1, 4)
plt.plot(acf_y[:100])  
plt.title('АКФ y(t)')
plt.xlabel('Запаздывание')
plt.ylabel('АКФ')
plt.grid()

plt.subplot(6, 1, 5)
plt.plot(f_y, Pxx_y)
plt.title('СПМ y(t)')
plt.xlabel('Частота (Гц)')
plt.ylabel('СПМ')
plt.grid()

plt.subplot(6, 1, 6)
plt.plot(t, A)
plt.title('Огибающая A(t)')
plt.xlabel('Время (с)')
plt.ylabel('Амплитуда')
plt.grid()

plt.figure(figsize=(12, 4))
plt.plot(ccf)
plt.title('ККФ между y(t) и y_channel(t)')
plt.xlabel('Запаздывание')
plt.ylabel('ККФ')
plt.grid()

plt.tight_layout()
plt.show()