import numpy as np
import matplotlib.pyplot as plt


fc = 2e9
c = 3e8
lam = c / fc
F = 16
V = 10
D = 1000
N = 100
NFFT = 128
alpha = np.pi / 6

dx = lam / F
n = np.arange(N)
t = n * dx / V
fs = 1 / (dx / V)
k = 2 * np.pi / lam
MSx = V * t * np.cos(alpha)
MSy = V * t * np.sin(alpha)
BSx, BSy = D, 0

dist = np.sqrt((BSx - MSx) ** 2 + (BSy - MSy) ** 2)

r = np.exp(-1j * k * dist)
R = np.fft.fftshift(np.fft.fft(r, NFFT))

freq_axis = np.arange(-NFFT // 2, NFFT // 2) * (fs / N)
freq_axis_fft = np.fft.fftshift(np.fft.fftfreq(NFFT, d=1 / fs))

doppler_idx = np.argmax(np.abs(R))
doppler_shift = freq_axis[doppler_idx]
doppler_shift_fft = freq_axis_fft[doppler_idx]

amplitude = np.abs(r)
phase = np.angle(r)

print("=== Задача 1: приём при движении MS ===")
print(f"Макс. амплитуда |r|: {np.max(amplitude):.6g}")
print("Фаза (первые 5 точек в радианах):", np.round(phase[:5], 6))
print(
    f"Смещение Допплера: {doppler_shift:.6f} Гц"
)
print(f"Смещение Допплера (FFT-ось): {doppler_shift_fft:.6f} Гц")
print()


np.random.seed(0)
Nsc = 200
Ntrk = 1000
BS = np.array([1000.0, 1000.0])

SC = np.random.uniform(-500, 500, (Nsc, 2))
trk_t = np.arange(Ntrk) * dx / V
MS_trk = np.vstack([V * trk_t * np.cos(0.0), V * trk_t * np.sin(0.0)]).T
dBSSC = np.linalg.norm(BS - SC, axis=1)

r_sum = np.empty(Ntrk, dtype=complex)
for idx, ms in enumerate(MS_trk):
    dSCMS = np.linalg.norm(SC - ms, axis=1)
    d_total = dBSSC + dSCMS
    r_sum[idx] = np.sum(np.exp(-1j * k * d_total))

R2 = np.fft.fftshift(np.fft.fft(r_sum, NFFT))

freq2 = np.arange(-NFFT // 2, NFFT // 2) * (fs / Ntrk)
freq2_fft = np.fft.fftshift(np.fft.fftfreq(NFFT, d=1 / fs))
doppler2_idx = np.argmax(np.abs(R2))
doppler2_shift = freq2[doppler2_idx]
doppler2_shift_fft = freq2_fft[doppler2_idx]

vals = np.abs(r_sum)
hist_counts, bin_edges = np.histogram(vals, bins=80)
hist_norm = hist_counts / len(vals)
sorted_vals = np.sort(vals)
cdf = np.arange(1, len(sorted_vals) + 1) / len(sorted_vals)

x = vals - np.mean(vals)
acf_full = np.correlate(x, x, mode="full")
acf_pos = acf_full[Ntrk - 1 :]
denom = np.arange(Ntrk, 0, -1)
acf_unbiased = acf_pos / denom
acf_normalized = acf_unbiased / acf_unbiased[0]
lags = np.arange(len(acf_normalized)) * (dx / V)


print("=== Задача 2: многолучевой приём (релеевское замирание) ===")
print(f"Число рассеивателей Nsc = {Nsc}, число точек трека Ntrk = {Ntrk}")
print(f"Средняя амплитуда по треку: {np.mean(vals):.6g}")
print(f"Макс. амплитуда по треку: {np.max(vals):.6g}")
print(
    f"Смещение Допплера: {doppler2_shift:.6f} Гц"
)
print(f"Смещение Допплера (FFT-ось): {doppler2_shift_fft:.6f} Гц")
print()


plt.figure(figsize=(10, 8))
plt.subplot(3, 1, 1)
plt.plot(t, amplitude, label="|r(t)|")
plt.title("Задача 1 — Амплитуда принятой огибающей")
plt.xlabel("Время, с")
plt.grid(True)

plt.subplot(3, 1, 2)
plt.plot(t, phase, label="phase")
plt.title("Задача 1 — Фаза принятой огибающей")
plt.xlabel("Время, с")
plt.grid(True)

plt.subplot(3, 1, 3)
plt.plot(
    freq_axis,
    np.abs(R),
    label="|R(f)|",
    linewidth=1.3,
)
plt.scatter(
    [doppler_shift],
    [np.abs(R).max()],
    color="k",
    zorder=10,
    label="Doppler peak",
)
plt.title("Задача 1 — Спектр (Допплер)")
plt.xlabel("Частота, Гц")
plt.legend()
plt.grid(True)
plt.tight_layout()


plt.figure(figsize=(8, 6))
plt.scatter(SC[:, 0], SC[:, 1], s=10, alpha=0.6, label="Scatterers (SC)")
plt.scatter(BS[0], BS[1], c="r", marker="^", s=80, label="BS (1000,1000)")

plt.plot(MS_trk[:, 0], MS_trk[:, 1], '-k', lw=2, label='MS track')
plt.title("Задача 2 — Рассеиватели, BS и фрагмент трека MS")
plt.axis("equal")
plt.grid(True)
plt.legend()
plt.tight_layout()

plt.figure(figsize=(12, 10))

plt.subplot(2, 2, 1)
plt.plot(np.arange(Ntrk) * (dx / V), vals)
plt.title("Задача 2 — Модуль принятого сигнала по треку")
plt.xlabel("Время, с")
plt.ylabel("|r_sum(t)|")
plt.grid(True)


plt.subplot(2, 2, 2)
plt.plot(np.arange(Ntrk) * (dx / V), np.angle(r_sum))
plt.title("Задача 2 — Фаза принятого сигнала по треку")
plt.xlabel("Время, с")
plt.ylabel("∠r_sum(t), рад")
plt.grid(True)


plt.subplot(2, 2, 3)
plt.hist(vals, bins=50, density=True, alpha=0.7, color="b", edgecolor="k")
plt.title("Функция распределения модуля принятого сигнала")
plt.xlabel("|r_sum|")
plt.ylabel("Плотность вероятности")
plt.grid(True)


plt.subplot(2, 2, 4)
plt.plot(freq2, np.abs(R2))
plt.title("Задача 2 — Спектр Допплера")
plt.xlabel("Частота, Гц")
plt.ylabel("|R2(f)|")
plt.grid(True)

plt.tight_layout()


plt.figure(figsize=(6, 4))
plt.plot(lags, acf_normalized)
plt.title("Задача 2 — Автокорреляция модуля принятого сигнала")
plt.xlabel("Лаг, с")
plt.ylabel("R(τ)")
plt.grid(True)
plt.tight_layout()


plt.show()
