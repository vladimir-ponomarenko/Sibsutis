import scipy.io as sp
import numpy as np
import os
import matplotlib.pyplot as plt
from scipy.fft import ifft
from mpl_toolkits.mplot3d import Axes3D


script_dir = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(script_dir, "H1.mat")
Hmatr = sp.loadmat(file_path)
h = Hmatr['H1']

BW = 20e6
Fs = BW
N = h.shape[0]

freq_mhz = (np.arange(N) * Fs / N) / 1e6
cols = np.arange(h.shape[1])

X_f, Y_f = np.meshgrid(cols, freq_mhz)
Z_f = np.abs(h)

fig1 = plt.figure(figsize=(12, 8))
ax1 = fig1.add_subplot(111, projection='3d')
ax1.plot_surface(X_f, Y_f, Z_f, cmap='viridis')
ax1.set_xlabel(' ')
ax1.set_ylabel('Частота, МГц')
ax1.set_zlabel('|H(f)|')
ax1.set_title('H(f)')

ht = ifft(h, axis=0)

tao_us = (np.arange(N) * (1/BW)) * 1e6

X_t, Y_t = np.meshgrid(cols, tao_us)
Z_t = np.abs(ht)
fig2 = plt.figure(figsize=(12, 8))
ax2 = fig2.add_subplot(111, projection='3d')

ax2.plot_surface(X_t, Y_t, Z_t, cmap='plasma')
ax2.set_xlabel('')
ax2.set_ylabel('Время, мкс')
ax2.set_zlabel('|h(t)|')
ax2.set_title('h(t)')

Nsn = h.shape[1]
abs_ht_squared = np.abs(ht)**2
sum_over_channels = np.sum(abs_ht_squared, axis=1)
P_tao = sum_over_channels / Nsn

fig3, ax3 = plt.subplots(figsize=(12, 8))
ax3.plot(tao_us, P_tao, color='red')
ax3.set_xlabel('Задержка τ, мкс')
ax3.set_ylabel('Мощность P(τ)')
ax3.set_title('Профиль мощности задержки')
ax3.grid(True)


tao_s = np.arange(N) * (1/BW)


Nsn = h.shape[1]
abs_ht_squared = np.abs(ht)**2
sum_over_channels = np.sum(abs_ht_squared, axis=1)
P_tao = sum_over_channels / Nsn

peak_power = np.max(P_tao)
threshold = peak_power * 10**(-25 / 10)
significant_indices = np.where(P_tao > threshold)[0]

if len(significant_indices) == 0:
    print("\nНе найдено значимых компонентов сигнала выше шумового порога.")
else:
    P_tao_filtered = P_tao[significant_indices]
    tao_s_filtered = tao_s[significant_indices]
    tau_M = tao_s_filtered[0]
    sum_p = np.sum(P_tao_filtered)
    mean_delay = np.sum(tao_s_filtered * P_tao_filtered) / sum_p
    T_D = mean_delay - tau_M
    numerator_S = np.sum(((tao_s_filtered - mean_delay)**2) * P_tao_filtered)
    S = np.sqrt(numerator_S / sum_p)
    print("\n--- Рассчитанные параметры канала ---")
    print(f"Среднее избыточное запаздывание (T_D): {T_D * 1e6:.4f} мкс")
    print(f"СКО разброса задержек (S): {S * 1e6:.4f} мкс")

plt.show()