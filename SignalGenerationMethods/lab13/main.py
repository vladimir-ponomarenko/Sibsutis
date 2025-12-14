import os
import numpy as np
import scipy.io as sp
import matplotlib.pyplot as plt


def add_noise(signal, target_snr_db):
    """Добавляет шум к сигналу заданного SNR"""
    sig_power = np.mean(np.abs(signal)**2)
    snr_linear = 10**(target_snr_db / 10.0)
    noise_power = sig_power / snr_linear
    noise = np.sqrt(noise_power/2) * (np.random.randn(*signal.shape) + 1j * np.random.randn(*signal.shape))
    return signal + noise

def calculate_ser(received_symbols, transmitted_symbols):
    """Считает Symbol Error Rate"""
    errors = 0
    total = received_symbols.size
    rx_signs = np.sign(received_symbols.real) + 1j*np.sign(received_symbols.imag)
    tx_signs = np.sign(transmitted_symbols.real) + 1j*np.sign(transmitted_symbols.imag)
    errors = np.sum(rx_signs != tx_signs)
    return errors / total

# ==============================================================================
# Задача 1: Загрузка и нормализация
# ==============================================================================
print("--- Задача 1: Загрузка и нормализация ---")
filename = "H16_uma_nlos_2.mat"
script_dir = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(script_dir, filename)
if not os.path.exists(file_path):
    print("Файл не найден.")
    # H_full_raw = np.random.randn(4, 4, 1, 1) + 1j * np.random.randn(4, 4, 1, 1)
else:
    mat_data = sp.loadmat(file_path)
    H_full_raw = mat_data['H16_16_Uma_NLOS']

Nr = 4  # Антенн на приемной стороне
Nt = 4  # Антенн на передающей стороне
sub_idx = 0
snap_idx = 0
H_raw = H_full_raw[:Nr, :Nt, sub_idx, snap_idx]
fro_norm = np.linalg.norm(H_raw, 'fro')
scale_factor = 1 / np.sqrt(Nr * Nt)
H = scale_factor * (H_raw / fro_norm)
H = H_raw / fro_norm * np.sqrt(Nr * Nt) 
print("Матрица канала H (нормализованная 4x4):")
print(H)

# ==============================================================================
# Задача 2: SVD разложение
# ==============================================================================
print("\n--- Задача 2: SVD разложение ---")
U, S, Vh = np.linalg.svd(H)
V = Vh.conj().T
print("Сингулярные числа (S):", S)

# ==============================================================================
# Задача 3: Ранг и матрицы
# ==============================================================================
print("\n--- Задача 3: Ранг и матрицы ---")
rank = np.sum(S > 1e-6)
print(f"Ранг канала: {rank}")
print(f"Максимальное сингулярное число: {np.max(S)}")
W_precoder_SVD = V[:, :rank]
W_combiner_SVD = U.conj().T[:rank, :]
print("Размер матрицы прекодирования:", W_precoder_SVD.shape)
print("Размер матрицы комбинирования:", W_combiner_SVD.shape)

# ==============================================================================
# Задача 4: Генерация сигнала
# ==============================================================================
print("\n--- Задача 4: Генерация сигнала ---")
num_bits = 10**4
bits = np.random.randint(0, 2, num_bits)
# QPSK
symbols_qpsk = []
for i in range(0, len(bits), 2):
    b0 = bits[i]
    b1 = bits[i+1] if i+1 < len(bits) else 0
    real = 1 if b0 == 0 else -1
    imag = 1 if b1 == 0 else -1
    symbols_qpsk.append((real + 1j*imag) / np.sqrt(2))
symbols_qpsk = np.array(symbols_qpsk)
num_symbols = len(symbols_qpsk)
# print(symbols_qpsk)
n_vecs = num_symbols // rank
x_streams = symbols_qpsk[:n_vecs*rank].reshape(rank, n_vecs)
print(f"Сформировано векторов символов: {n_vecs}")

# ==============================================================================
# Задача 5: Прекодирование (SVD)
# ==============================================================================
print("\n--- Задача 5: Прекодирование (SVD) ---")
x_transmitted = W_precoder_SVD @ x_streams
# print(x_transmitted)

# ==============================================================================
# Задача 6: Прохождение канала (SVD)
# ==============================================================================
print("\n--- Задача 6: Прохождение канала (SVD) ---")
y_received_clean = H @ x_transmitted
y_received_noisy_10dB = add_noise(y_received_clean, 10)
# print(y_received_noisy_10dB)

plt.figure(figsize=(6, 6))
plt.scatter(y_received_noisy_10dB[0, :1000].real, y_received_noisy_10dB[0, :1000].imag, alpha=0.5, s=10)
plt.title("SVD: Принятый сигнал")
plt.grid(True)
plt.xlabel("I")
plt.ylabel("Q")
plt.axis('equal')
plt.show()

# ==============================================================================
# Задача 7: Комбинирование (SVD)
# ==============================================================================
print("\n--- Задача 7: Комбинирование (SVD) ---")
y_combined = W_combiner_SVD @ y_received_noisy_10dB
y_estimated_svd = np.zeros_like(y_combined)
for i in range(rank):
    y_estimated_svd[i, :] = y_combined[i, :] / S[i]

plt.figure(figsize=(6, 6))
plt.scatter(y_estimated_svd[0, :1000].real, y_estimated_svd[0, :1000].imag, c='r', alpha=0.5, s=10)
plt.title(f"SVD: Сигнал после обработки")
plt.grid(True)
plt.xlabel("I")
plt.ylabel("Q")
plt.axis('equal')
plt.show()

# ==============================================================================
# Задача 8: SER vs SNR (SVD)
# ==============================================================================
print("\n--- Задача 8: SER vs SNR (SVD) ---")
snr_range = range(0,25)
ser_svd = []
constellation = np.array([1+1j, 1-1j, -1+1j, -1-1j]) / np.sqrt(2)
for snr in snr_range:
    y_noisy = add_noise(y_received_clean, snr)
    y_comb = W_combiner_SVD @ y_noisy
    y_est = np.zeros_like(y_comb)
    for i in range(rank):
        y_est[i, :] = y_comb[i, :] / S[i]
    ser = calculate_ser(y_est, x_streams)
    ser_svd.append(ser)

plt.figure(figsize=(8, 5))
plt.semilogy(snr_range, ser_svd, 'o-', label='SVD')
plt.title("SVD: Вероятность ошибки символа")
plt.xlabel("SNR, дБ")
plt.ylabel("SER")
plt.grid(True, which="both")
plt.legend()
plt.show()

# ==============================================================================
# Задача 9: ZF Передача
# ==============================================================================
print("\n--- Задача 9: ZF Передача ---")
num_streams_zf = rank
x_streams_zf = x_streams
x_transmitted_zf = np.zeros((Nt, n_vecs), dtype=complex)
x_transmitted_zf[:num_streams_zf, :] = x_streams_zf

# ==============================================================================
# Задача 10: ZF Канал + Шум
# ==============================================================================
print("\n--- Задача 10: ZF Канал + Шум ---")
y_received_zf_clean = H @ x_transmitted_zf
y_received_zf_noisy = add_noise(y_received_zf_clean, 10)

plt.figure(figsize=(6, 6))
plt.scatter(y_received_zf_noisy[0, :1000].real, y_received_zf_noisy[0, :1000].imag, alpha=0.5, s=10)
plt.title("ZF: Принятый сигнал")
plt.grid(True)
plt.axis('equal')
plt.show()

# ==============================================================================
# Задача 11: ZF Обработка
# ==============================================================================
print("\n--- Задача 11: ZF Обработка ---")
W_zf = np.linalg.pinv(H)

print("Размер матрицы ZF:", W_zf.shape)

# s_hat = W_zf * y
x_estimated_zf_full = W_zf @ y_received_zf_noisy
x_estimated_zf = x_estimated_zf_full[:num_streams_zf, :]

plt.figure(figsize=(6, 6))
plt.scatter(x_estimated_zf[0, :1000].real, x_estimated_zf[0, :1000].imag, c='g', alpha=0.5, s=10)
plt.title("ZF: Сигнал после комбинирования (Слой 1) (SNR 10 дБ)")
plt.grid(True)
plt.xlabel("I")
plt.ylabel("Q")
plt.axis('equal')
plt.show()

# ==============================================================================
# Задача 12: SER vs SNR (ZF)
# ==============================================================================
print("\n--- Задача 12: SER vs SNR (ZF) ---")
ser_zf = []

for snr in snr_range:
    y_noisy = add_noise(y_received_zf_clean, snr)
    x_est_full = W_zf @ y_noisy
    x_est = x_est_full[:num_streams_zf, :]
    ser = calculate_ser(x_est, x_streams_zf)
    ser_zf.append(ser)

plt.figure(figsize=(8, 5))
plt.semilogy(snr_range, ser_svd, 'o-', label='SVD MIMO')
plt.semilogy(snr_range, ser_zf, 's--', label='ZF MIMO')
plt.title("Сравнение SER: SVD vs ZF")
plt.xlabel("SNR, дБ")
plt.ylabel("SER")
plt.grid(True, which="both")
plt.legend()
plt.show()

# ==============================================================================
# Задача 14: MMSE Передача (формирование)
# ==============================================================================
print("\n--- Задача 14: MMSE Передача ---")
x_transmitted_mmse = x_transmitted_zf

print("Данные для MMSE сформированы (аналогично ZF).")

# ==============================================================================
# Задача 15: MMSE Прием + Шум
# ==============================================================================
print("\n--- Задача 15: MMSE Канал + Шум ---")
y_received_mmse_clean = H @ x_transmitted_mmse

# SNR = P_signal / P_noise => P_noise (sigma_n^2) = P_signal / SNR_linear
target_snr_mmse = 10.0
sig_power_mmse = np.mean(np.abs(y_received_mmse_clean)**2)
snr_lin_mmse = 10**(target_snr_mmse / 10.0)
noise_power_mmse = sig_power_mmse / snr_lin_mmse

print(f"Мощность сигнала: {sig_power_mmse:.4f}")
print(f"Дисперсия шума (sigma_n^2) для 10 дБ: {noise_power_mmse:.4f}")

noise_mmse = np.sqrt(noise_power_mmse/2) * (np.random.randn(*y_received_mmse_clean.shape) + 1j * np.random.randn(*y_received_mmse_clean.shape))
y_received_mmse_noisy = y_received_mmse_clean + noise_mmse

plt.figure(figsize=(6, 6))
plt.scatter(y_received_mmse_noisy[0, :1000].real, y_received_mmse_noisy[0, :1000].imag, alpha=0.5, s=10)
plt.title(f"MMSE: Принятый сигнал на антенне (SNR {target_snr_mmse} дБ)")
plt.grid(True)
plt.axis('equal')
plt.xlabel("I")
plt.ylabel("Q")
plt.show()

# ==============================================================================
# Задача 16: Матрица комбинирования MMSE
# ==============================================================================
print("\n--- Задача 16: Матрица комбинирования MMSE ---")
I_mat = np.eye(Nt)
# noise_power_mmse - это sigma_n^2

term_inv = np.linalg.inv(H.conj().T @ H + noise_power_mmse * I_mat)
W_mmse = term_inv @ H.conj().T

print("Размер матрицы MMSE:", W_mmse.shape)

x_estimated_mmse_full = W_mmse @ y_received_mmse_noisy
x_estimated_mmse = x_estimated_mmse_full[:num_streams_zf, :]

plt.figure(figsize=(6, 6))
plt.scatter(x_estimated_mmse[0, :1000].real, x_estimated_mmse[0, :1000].imag, c='m', alpha=0.5, s=10)
plt.title(f"MMSE: Сигнал после комбинирования (SNR {target_snr_mmse} дБ)")
plt.grid(True)
plt.axis('equal')
plt.xlabel("I")
plt.ylabel("Q")
plt.show()

# ==============================================================================
# Задача 17: Сравнение SER (SVD, ZF, MMSE)
# ==============================================================================
print("\n--- Задача 17: Сравнение SER для 0-12 дБ ---")
snr_range_task17 = range(0, 13)

ser_svd_17 = []
ser_zf_17 = []
ser_mmse_17 = []
p_signal_zf = np.mean(np.abs(H @ x_transmitted_zf)**2)

for snr in snr_range_task17:
    snr_lin = 10**(snr / 10.0)
    noise_var = p_signal_zf / snr_lin
    noise = np.sqrt(noise_var/2) * (np.random.randn(*y_received_zf_clean.shape) + 1j * np.random.randn(*y_received_zf_clean.shape))

    # --- 2. SVD ---
    y_svd_noisy = (H @ x_transmitted) + noise
    y_comb_svd = W_combiner_SVD @ y_svd_noisy
    y_est_svd = np.zeros_like(y_comb_svd)
    for i in range(rank):
        y_est_svd[i, :] = y_comb_svd[i, :] / S[i]
    ser_svd_17.append(calculate_ser(y_est_svd, x_streams))

    # --- 3. ZF ---
    y_zf_noisy = (H @ x_transmitted_zf) + noise
    x_est_zf_full = W_zf @ y_zf_noisy
    ser_zf_17.append(calculate_ser(x_est_zf_full[:rank], x_streams_zf))

    # --- 4. MMSE ---
    W_mmse_curr = np.linalg.inv(H.conj().T @ H + noise_var * np.eye(Nt)) @ H.conj().T
    x_est_mmse_full = W_mmse_curr @ y_zf_noisy
    ser_mmse_17.append(calculate_ser(x_est_mmse_full[:rank], x_streams_zf))

plt.figure(figsize=(8, 6))
plt.semilogy(snr_range_task17, ser_svd_17, 'o-', label='SVD (Optimal)', linewidth=2)
plt.semilogy(snr_range_task17, ser_zf_17, 's--', label='ZF (Zero Forcing)', linewidth=2)
plt.semilogy(snr_range_task17, ser_mmse_17, 'd-.', label='MMSE', linewidth=2)

plt.title("Сравнение методов приема (SVD, ZF, MMSE)")
plt.xlabel("SNR, дБ")
plt.ylabel("Symbol Error Rate (SER)")
plt.grid(True, which="both")
plt.legend()
plt.show()

print("Выполнение всех задач завершено.")