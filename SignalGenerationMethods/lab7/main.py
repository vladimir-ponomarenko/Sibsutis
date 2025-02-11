import numpy as np
import matplotlib.pyplot as plt


T = 1e-4
Nc = 16
df = 1/T
ts = T/Nc

t = ts * np.arange(0, Nc)

k = 1
s = 1/np.sqrt(T) * np.exp(1j * 2 * np.pi * k * df * t)
plt.figure(1)
plt.title('Пример одной поднесущей (реальная часть)')
plt.plot(t, s.real)
plt.xlabel('Время, с')
plt.ylabel('Амплитуда')
plt.grid(True)

sc_matr = np.zeros((Nc, len(t)), dtype=complex)
for k in range(Nc):
    sk_k = 1/np.sqrt(T) * np.exp(1j * 2 * np.pi * k * df * t)
    sc_matr[k, :] = sk_k

sd = np.sign(np.random.rand(Nc) - 0.5) + 1j * np.sign(np.random.rand(Nc) - 0.5)
xt = np.zeros(len(t), dtype=complex)
for k in range(Nc):
    sc = sc_matr[k, :]
    xt = xt + sd[k] * sc

plt.figure(2)
plt.title('OFDM символ (метод суммирования)')
plt.plot(t, xt.real)
plt.xlabel('Время, с')
plt.ylabel('Амплитуда')
plt.grid(True)

xt2 = (Nc / np.sqrt(T)) * np.fft.ifft(sd, 16)

plt.figure(3)
plt.title('OFDM символ (метод ОДПФ)')
plt.plot(t, xt2.real)
plt.xlabel('Время, с')
plt.ylabel('Амплитуда')
plt.grid(True)

n = 3
sr = ts * np.sum(xt * np.conjugate(sc_matr[n, :]))

print(f"--- Демодуляция методом корреляции (для поднесущей n={n}) ---")
print(f"Переданный символ sd[{n}]: {np.round(sd[n], 2)}")
print(f"Принятый символ sr:       {np.round(sr, 2)}")
print("-" * 40)

sr2 = (np.sqrt(T) / Nc) * np.fft.fft(xt)

print("--- Демодуляция методом ДПФ (для всех поднесущих) ---")
print("Переданные символы (sd):")
print(np.round(sd, 2))
print("\nПринятые символы (sr2):")
print(np.round(sr2, 2))

plt.show()