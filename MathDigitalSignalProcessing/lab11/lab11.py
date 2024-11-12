from scipy.fftpack import fft, ifft, fftshift
import numpy as np
import matplotlib.pyplot as plt

# --- Задание 1 ---
fc1 = 10
fs1 = 32 * fc1
t1 = np.arange(0, 2, 1/fs1)
x1 = np.sin(2 * np.pi * fc1 * t1)

fc2 = 12 * 10
fs2 = 32 * fc2
t2 = np.arange(0, 2, 1/fs2)
x2 = np.sin(2 * np.pi * fc2 * t2)

plt.figure(1)
plt.subplot(2, 1, 1)
plt.plot(t1, x1, label='Сигнал 1')
plt.xlabel('$t=nT_s$')
plt.ylabel('$x[n]$')
plt.title('Временная диаграмма сигнала 1')

plt.subplot(2, 1, 2)
plt.plot(t2, x2, label='Сигнал 2')
plt.xlabel('$t=nT_s$')
plt.ylabel('$x[n]$')
plt.title('Временная диаграмма сигнала 2')
plt.tight_layout()


# --- Задание 2 ---
N2 = 512
X4 = fft(x1, N2) / N2
df2 = fs1 / N2
k2 = np.arange(0, N2)
kf4 = k2 * df2
k_signal4 = np.argmin(np.abs(kf4 - fc1))
print(f"При N = {N2}, шаг частот: {df2} Гц. Сигнал в точке ДПФ: {k_signal4}")

plt.figure(4)
plt.stem(kf4, abs(X4))
plt.xlabel('Гц')
plt.ylabel('$|X[k]|$')
plt.title('ДПФ с N=512')
N = 256
X = fft(x1, N) / N

df = fs1 / N
k = np.arange(0, N)
kf = k * df

k_signal = np.argmin(np.abs(kf - fc1))

print(f"Шаг частот между точками ДПФ: {df} Гц")
print(f"Сигнал находится в точке ДПФ с индексом: {k_signal}")

plt.figure(2)
plt.subplot(2, 1, 1)
plt.stem(kf, abs(X))
plt.xlabel('Гц')
plt.ylabel('$|X[k]|$')
plt.title('ДПФ сигнала 1')

X2 = fft(x2, N) / N

df2 = fs2 / N
kf2 = k * df2

k_signal2 = np.argmin(np.abs(kf2 - fc2))

print(f"Шаг частот между точками ДПФ: {df2} Гц")
print(f"Сигнал находится в точке ДПФ с индексом: {k_signal2}")

plt.subplot(2, 1, 2)
plt.stem(kf2, abs(X2))
plt.xlabel('Гц')
plt.ylabel('$|X[k]|$')
plt.title('ДПФ сигнала 2')


# --- Задание 3 ---
fc3 = 2 * fc1
fs3 = 32 * fc3
x3 = np.sin(2 * np.pi * fc3 * t1)
X3 = fft(x3, N) / N
kf3 = k*fs3/N

k_signal3 = np.argmin(np.abs(kf3 - fc3))
print(f"Для сигнала с частотой {fc3} Гц, индекс точки ДПФ: {k_signal3}")

plt.figure(3)
plt.stem(kf3, abs(X3))
plt.xlabel('Гц')
plt.ylabel('$|X[k]|$')
plt.title('ДПФ сигнала с удвоенной частотой')


# --- Задание 4 ---
N2 = 512
X4 = fft(x1, N2) / N2
df2 = fs1 / N2
k2 = np.arange(0, N2)
kf4 = k2 * df2
k_signal4 = np.argmin(np.abs(kf4 - fc1))
print(f"При N = {N2}, шаг частот: {df2} Гц. Сигнал в точке ДПФ: {k_signal4}")

plt.figure(4)
plt.stem(kf4, abs(X4))
plt.xlabel('Гц')
plt.ylabel('$|X[k]|$')
plt.title('ДПФ с N=512')


# --- Задание 5 ---
fc4 = 5
x5 = x1 + np.sin(2 * np.pi * fc4 * t1)
X5 = fft(x5, N) / N
plt.figure(5)
plt.stem(kf, abs(X5))
plt.xlabel('Гц')
plt.ylabel('$|X[k]|$')
plt.title('ДПФ суммы двух колебаний')


# --- Задание 6 ---
X6 = np.array([0, 0, 1, 0, 0, 0, 0, 0])
x1 = ifft(X6) * len(X6)

X7 = np.array([0, 0, 1j, 0, 0, 0, 0, 0])
x2 = ifft(X7) * len(X7)

X8 = np.array([0, 0, -1j, 0, 0, 0, 0, 0])
x3 = ifft(X8) * len(X8)

X9 = np.array([0, 0, 2-1j, 0, 0, 0, 0, 0])
x4 = ifft(X9) * len(X9)

X10 = np.array([0, 0, 2+1j, 0, 0, 0, 0, 0])
x5 = ifft(X10) * len(X10)

X11 = np.zeros(16, dtype=complex)
X11[3] = 1
x6 = ifft(X11) * len(X11)



plt.figure(6)
plt.subplot(3, 2, 1)
plt.stem(np.real(x1))
plt.title('ОДПФ X6')

plt.subplot(3, 2, 2)
plt.stem(np.real(x2))
plt.title('ОДПФ X7')

plt.subplot(3, 2, 3)
plt.stem(np.real(x3))
plt.title('ОДПФ X8')

plt.subplot(3, 2, 4)
plt.stem(np.real(x4))
plt.title('ОДПФ X9')

plt.subplot(3, 2, 5)
plt.stem(np.real(x5))
plt.title('ОДПФ X10')

plt.subplot(3, 2, 6)
plt.stem(np.real(x6))
plt.title('ОДПФ X11 (16 точек)')

plt.tight_layout()
plt.show()
