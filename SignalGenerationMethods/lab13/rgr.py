import os
import numpy as np
import scipy.io as sp
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d

# ==============================================================================
# Вспомогательные функции
# ==============================================================================

def add_noise_return_noise(signal, target_snr_db):
    """
    Добавляет шум к сигналу заданного SNR.
    Возвращает: зашумленный сигнал, сам шум, мощность шума (sigma^2).
    """
    sig_power = np.mean(np.abs(signal)**2)

    snr_linear = 10**(target_snr_db / 10.0)
    noise_power = sig_power / snr_linear

    noise = np.sqrt(noise_power/2) * (np.random.randn(*signal.shape) + 1j * np.random.randn(*signal.shape))

    return signal + noise, noise, noise_power

def calculate_ser(received_symbols, transmitted_symbols):
    """Считает Symbol Error Rate (для QPSK)"""
    rx_signs = np.sign(received_symbols.real) + 1j*np.sign(received_symbols.imag)
    tx_signs = np.sign(transmitted_symbols.real) + 1j*np.sign(transmitted_symbols.imag)
    errors = np.sum(rx_signs != tx_signs)
    return errors / received_symbols.size

# ==============================================================================
# Пункт 1: Загрузка файла и нормализация
# ==============================================================================
print("--- Пункт 1: Загрузка канала 8x8 и нормализация ---")

filename = "H16_uma_nlos_2.mat"
script_dir = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(script_dir, filename)

K_subcarriers = 64  # Всего поднесущих

if not os.path.exists(file_path):
    print("Файл не найден. Генерируем случайную реализацию.")
    H_full_raw = np.random.randn(16, 16, K_subcarriers, 1) + 1j * np.random.randn(16, 16, K_subcarriers, 1)
else:
    mat_data = sp.loadmat(file_path)
    # Берем первый массив из файла
    keys = [key for key in mat_data.keys() if not key.startswith('_')]
    H_full_raw = mat_data[keys[0]]

Nr = 8
Nt = 8
snapshot_idx = 0

H_block = H_full_raw[:Nr, :Nt, :K_subcarriers, snapshot_idx]

fro_norm = np.linalg.norm(H_block)
H_true_all = H_block / fro_norm

print(f"Канал загружен. Размер: {H_true_all.shape}. Норма ||H||: {np.linalg.norm(H_true_all):.2f}")


# ==============================================================================
# Пункт 2: Оценка канала (LS + Интерполяция)
# ==============================================================================
print("\n--- Пункт 2: Оценка канала LS и выбор поднесущей ---")

P_step = 4
pilot_indices = np.arange(0, K_subcarriers, P_step)
data_indices = np.arange(0, K_subcarriers)
pilot_val = 1 + 1j

H_est_all = np.zeros((Nr, Nt, K_subcarriers), dtype=complex)
SNR_pilot = 20 #

for r in range(Nr):
    for t in range(Nt):
        H_rt = H_true_all[r, t, :]

        Y_pilots_clean = H_rt[pilot_indices] * pilot_val
        Y_pilots, _, _ = add_noise_return_noise(Y_pilots_clean, SNR_pilot)

        # LS оценка: H = Y / X
        H_ls = Y_pilots / pilot_val

        # Интерполяция
        interpolator = interp1d(pilot_indices, H_ls, kind='linear', fill_value="extrapolate")
        H_est_all[r, t, :] = interpolator(data_indices)

chosen_sub = 32
H_est = H_est_all[:, :, chosen_sub]
H_true = H_true_all[:, :, chosen_sub]

print("Оценка выполнена. Матрицы сформированы.")

# ==============================================================================
# Пункт 3: SVD вычисление
# ==============================================================================
print("\n--- Пункт 3: SVD матрицы канала (по оценке) ---")
U_est, S_est, Vh_est = np.linalg.svd(H_est)
V_est = Vh_est.conj().T

# ==============================================================================
# Пункт 4: Ранг и диаграмма
# ==============================================================================
print("\n--- Пункт 4: Ранг и диаграмма сингулярных чисел ---")
rank = np.sum(S_est > 1e-9)
print(f"Ранг канала: {rank}")

W_prec_svd = V_est[:, :rank]
W_comb_svd = U_est.conj().T[:rank, :]

plt.figure(figsize=(6, 4))
plt.stem(S_est)
plt.title("Диаграмма сингулярных чисел")
plt.xlabel("Индекс")
plt.ylabel("Значение")
plt.grid(True)
plt.show()

# ==============================================================================
# Пункт 5: Формирование бит и векторов (SVD)
# ==============================================================================
print("\n--- Пункт 5: Формирование сигнала (SVD) ---")
num_bits = 10**4
bits = np.random.randint(0, 2, num_bits)

symbols = []
for i in range(0, len(bits), 2):
    val = (1 if bits[i]==0 else -1) + 1j*(1 if bits[i+1]==0 else -1)
    symbols.append(val / np.sqrt(2))
symbols = np.array(symbols)

n_vecs = len(symbols) // rank
x_streams = symbols[:n_vecs*rank].reshape(rank, n_vecs)

# ==============================================================================
# Пункт 6: Прекодирование Tx = Vx
# ==============================================================================
print("\n--- Пункт 6: Прекодирование и диаграмма ---")
Tx_svd = W_prec_svd @ x_streams

plt.figure(figsize=(5, 5))
plt.scatter(Tx_svd[0, :1000].real, Tx_svd[0, :1000].imag, s=5)
plt.title("Сигнальная диаграмма прекодированного сигнала (Tx)")
plt.axis('equal')
plt.grid(True)
plt.show()

# ==============================================================================
# Пункт 7: Передача y = HTx
# ==============================================================================
print("\n--- Пункт 7: Передача сигнала ---")
y_svd_clean = H_true @ Tx_svd

# ==============================================================================
# Пункт 8: Шум и диаграмма приема
# ==============================================================================
print("\n--- Пункт 8: Прием с шумом 10 дБ ---")
y_svd_noisy, _, _ = add_noise_return_noise(y_svd_clean, 10)

plt.figure(figsize=(5, 5))
plt.scatter(y_svd_noisy[0, :1000].real, y_svd_noisy[0, :1000].imag, s=5, alpha=0.5)
plt.title("Принятый сигнал на одной антенне")
plt.axis('equal')
plt.grid(True)
plt.show()

# ==============================================================================
# Пункт 9: Комбинирование SVD
# ==============================================================================
print("\n--- Пункт 9: Комбинирование SVD ---")
x_hat_svd_raw = W_comb_svd @ y_svd_noisy

# Эквализация (деление на S) для корректного созвездия
x_hat_svd = np.zeros_like(x_hat_svd_raw)
for i in range(rank):
    x_hat_svd[i, :] = x_hat_svd_raw[i, :] / S_est[i]

plt.figure(figsize=(5, 5))
plt.scatter(x_hat_svd[0, :1000].real, x_hat_svd[0, :1000].imag, c='r', s=5, alpha=0.5)
plt.title("SVD: Сигнал после комбинирования")
plt.axis('equal')
plt.grid(True)
plt.show()

# ==============================================================================
# Пункт 10: SER vs SNR (SVD)
# ==============================================================================
print("\n--- Пункт 10: График SER (SVD) ---")
snr_range = range(0, 13)
ser_svd = []

for snr in snr_range:
    y_n, _, _ = add_noise_return_noise(y_svd_clean, snr)
    y_c = W_comb_svd @ y_n
    y_final = np.zeros_like(y_c)
    for i in range(rank):
        y_final[i, :] = y_c[i, :] / S_est[i]
    ser_svd.append(calculate_ser(y_final, x_streams))

plt.figure(figsize=(6, 4))
plt.semilogy(snr_range, ser_svd, 'o-')
plt.title("P=f(SNR) для SVD")
plt.xlabel("SNR, дБ")
plt.ylabel("Вероятность ошибки (SER)")
plt.grid(True, which='both')
plt.show()

# ==============================================================================
# Пункт 11: ZF Передача
# ==============================================================================
print("\n--- Пункт 11: ZF Передача ---")
num_streams_zf = rank
x_streams_zf = x_streams
Tx_zf = np.zeros((Nt, n_vecs), dtype=complex)
Tx_zf[:num_streams_zf, :] = x_streams_zf

y_zf_clean = H_true @ Tx_zf

# ==============================================================================
# Пункт 12: ZF Прием + Шум
# ==============================================================================
print("\n--- Пункт 12: ZF Прием (10 дБ) ---")
y_zf_noisy, _, _ = add_noise_return_noise(y_zf_clean, 10)

plt.figure(figsize=(5, 5))
plt.scatter(y_zf_noisy[0, :1000].real, y_zf_noisy[0, :1000].imag, s=5, alpha=0.5)
plt.title("ZF: Принятый сигнал на одной антенне")
plt.axis('equal')
plt.grid(True)
plt.show()

# ==============================================================================
# Пункт 13: ZF Комбинирование
# ==============================================================================
print("\n--- Пункт 13: ZF Матрица и комбинирование ---")
# W_zf = pinv(H_est)
W_zf = np.linalg.pinv(H_est)

x_hat_zf_full = W_zf @ y_zf_noisy
x_hat_zf = x_hat_zf_full[:num_streams_zf, :]

plt.figure(figsize=(5, 5))
plt.scatter(x_hat_zf[0, :1000].real, x_hat_zf[0, :1000].imag, c='g', s=5, alpha=0.5)
plt.title("ZF: Сигнал после комбинирования")
plt.axis('equal')
plt.grid(True)
plt.show()

# ==============================================================================
# Пункт 14: SER vs SNR (ZF)
# ==============================================================================
print("\n--- Пункт 14: График SER (ZF) ---")
ser_zf = []
for snr in snr_range:
    y_n, _, _ = add_noise_return_noise(y_zf_clean, snr)
    x_hat = (W_zf @ y_n)[:num_streams_zf, :]
    ser_zf.append(calculate_ser(x_hat, x_streams_zf))

plt.figure(figsize=(6, 4))
plt.semilogy(snr_range, ser_zf, 's-', color='green')
plt.title("P=f(SNR) для ZF")
plt.xlabel("SNR, дБ")
plt.ylabel("SER")
plt.grid(True, which='both')
plt.show()

# ==============================================================================
# Пункт 15: MMSE Передача
# ==============================================================================
print("\n--- Пункт 15: MMSE Передача ---")
Tx_mmse = Tx_zf
y_mmse_clean = H_true @ Tx_mmse

# ==============================================================================
# Пункт 16: MMSE Шум и диаграмма
# ==============================================================================
print("\n--- Пункт 16: MMSE Шум (10 дБ) ---")
y_mmse_noisy, _, noise_power_val = add_noise_return_noise(y_mmse_clean, 10)

plt.figure(figsize=(5, 5))
plt.scatter(y_mmse_noisy[0, :1000].real, y_mmse_noisy[0, :1000].imag, s=5, alpha=0.5)
plt.title("MMSE: Принятый сигнал на одной антенне")
plt.axis('equal')
plt.grid(True)
plt.show()

# ==============================================================================
# Пункт 17: MMSE Матрица и комбинирование
# ==============================================================================
print("\n--- Пункт 17: MMSE Комбинирование ---")
# W_mmse = (H^H H + sigma^2 I)^-1 H^H
I_mat = np.eye(Nt)
H_herm = H_est.conj().T
W_mmse = np.linalg.inv(H_herm @ H_est + noise_power_val * I_mat) @ H_herm

x_hat_mmse = (W_mmse @ y_mmse_noisy)[:num_streams_zf, :]

plt.figure(figsize=(5, 5))
plt.scatter(x_hat_mmse[0, :1000].real, x_hat_mmse[0, :1000].imag, c='m', s=5, alpha=0.5)
plt.title("MMSE: Сигнал после комбинирования")
plt.axis('equal')
plt.grid(True)
plt.show()

# ==============================================================================
# Пункт 18: Итоговое сравнение SER
# ==============================================================================
print("\n--- Пункт 18: Итоговое сравнение ---")
ser_mmse = []

P_sig_avg = np.mean(np.abs(y_mmse_clean)**2)

for snr in snr_range:
    y_n, _, n_pwr = add_noise_return_noise(y_mmse_clean, snr)

    W_curr = np.linalg.inv(H_herm @ H_est + n_pwr * I_mat) @ H_herm

    x_hat = (W_curr @ y_n)[:num_streams_zf, :]
    ser_mmse.append(calculate_ser(x_hat, x_streams_zf))

plt.figure(figsize=(10, 7))
plt.semilogy(snr_range, ser_svd, 'o-', label='SVD')
plt.semilogy(snr_range, ser_zf, 's--', label='ZF')
plt.semilogy(snr_range, ser_mmse, 'd-.', label='MMSE')
plt.title("Сравнение вероятности ошибки (SER) для SVD, ZF, MMSE")
plt.xlabel("SNR, дБ")
plt.ylabel("SER")
plt.grid(True, which='both')
plt.legend()
plt.show()

print("Все пункты выполнены.")