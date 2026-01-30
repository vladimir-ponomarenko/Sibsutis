import os
import numpy as np
import scipy.io as sp
import numpy.linalg as la
import matplotlib.pyplot as plt

# ==============================================================================
# Вспомогательные функции
# ==============================================================================
def add_noise_to_signal(signal, snr_db):
    """Добавляет шум к сигналу"""
    sig_power = np.mean(np.abs(signal)**2)
    if sig_power == 0: return signal, 0
    snr_lin = 10**(snr_db / 10.0)
    noise_power = sig_power / snr_lin
    noise = np.sqrt(noise_power/2) * (np.random.randn(*signal.shape) + 1j * np.random.randn(*signal.shape))
    return signal + noise, noise_power

def calculate_ser(received, transmitted):
    """Расчет SER для QPSK"""
    rx = received.flatten()
    tx = transmitted.flatten()
    rx_signs = np.sign(rx.real) + 1j*np.sign(rx.imag)
    tx_signs = np.sign(tx.real) + 1j*np.sign(tx.imag)
    return np.sum(rx_signs != tx_signs) / rx.size

# ==============================================================================
# Пункт 1: Загрузка данных MU-MIMO
# ==============================================================================
print("--- 1. Загрузка данных ---")
filename = "H16_4_35.mat"
script_dir = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(script_dir, filename)

if not os.path.exists(file_path):
    print("Файл не найден. Генерируем данные.")
    h_full = np.random.randn(16, 400, 35) + 1j * np.random.randn(16, 400, 35)
else:
    Hmatr = sp.loadmat(file_path)
    vals = list(Hmatr.values())
    h_full = next((v for v in vals if isinstance(v, np.ndarray) and v.ndim == 3), None)

print(f"Размерность данных канала: {h_full.shape}")

subcarrier_idx = 100 
user_indices = [0, 1, 2, 3] # 4 абонента

H_true_list = []
for u_idx in user_indices:
    h_vec = h_full[:, subcarrier_idx, u_idx]
    h_vec = h_vec / la.norm(h_vec)
    H_true_list.append(h_vec)

H_true = np.vstack(H_true_list)
print("Матрица исходного канала H_true сформирована.")


# ==============================================================================
# Пункт 2: SRS и Оценка канала (LS)
# ==============================================================================
print("\n--- 2. Моделирование SRS и LS-оценка ---")
len_srs = 24
srs_bits = np.random.randint(0, 2, len_srs * 2)
SRS_seq = (1/np.sqrt(2)) * ((2*srs_bits[::2]-1) + 1j*(2*srs_bits[1::2]-1))

H_est_list = []
SNR_SRS_dB = 15

for i, u_idx in enumerate(user_indices):
    
    h_user_true = H_true[i, :]
    Y_received_srs = np.outer(h_user_true, SRS_seq)
    
    Y_received_srs_noisy, _ = add_noise_to_signal(Y_received_srs, SNR_SRS_dB)
    
    # LS Оценка: H_est = Y / X.
    # Так как X (SRS) известен, и мы в частотной области:
    # H_est = Y * conj(SRS) / |SRS|^2. Так как |SRS|=1, то H_est = Y * conj(SRS) / length
    # LS: h_est = mean(y_received / srs_symbol)
    
    H_ls_raw = Y_received_srs_noisy / SRS_seq[np.newaxis, :] # (16, 24)
    
    h_user_est = np.mean(H_ls_raw, axis=1)
    
    H_est_list.append(h_user_est)

H_est = np.vstack(H_est_list) # Матрица оценки (4, 16)
print(f"Оценка канала выполнена методом LS (SNR={SNR_SRS_dB} дБ).")


# ==============================================================================
# Пункт 3: Вычисление векторов прекодирования (Исходный vs Оценка)
# ==============================================================================
print("\n--- 3. Вычисление векторов прекодирования ---")

def calc_zf_precoder(H_channel):
    """
    H_channel: матрица (Users x Antennas) (4x16)
    Возвращает W: матрица (Antennas x Users) (16x4)
    """
    # H^H
    H_herm = H_channel.conj().T
    # Inv(H * H^H)
    Gram_inv = la.inv(H_channel @ H_herm)
    # W = H^H * Inv(...)
    W = H_herm @ Gram_inv
    
    for col in range(W.shape[1]):
        W[:, col] = W[:, col] / la.norm(W[:, col])
    return W

W_ideal = calc_zf_precoder(H_true)

W_est = calc_zf_precoder(H_est)

print("Рассчитаны векторы прекодирования для H_true и H_est.")


# ==============================================================================
# Пункт 4: Проверка подавления интерференции
# ==============================================================================
print("\n--- 4. Проверка подавления интерференции ---")

# Функция для вывода SIR
def check_interference(H_ch, W_prec, name):
    Eff = H_ch @ W_prec
    
    diag_pwr = np.sum(np.abs(np.diag(Eff))**2)
    total_pwr = np.sum(np.abs(Eff)**2)
    interf_pwr = total_pwr - diag_pwr
    
    # SIR
    if interf_pwr < 1e-15: 
        sir = 100.0 # Бесконечность
    else:
        sir = 10 * np.log10(diag_pwr / interf_pwr)
        
    print(f"[{name}] SIR: {sir:.2f} дБ")
    print(f"Матрица амплитуд (первые 2x2):\n{np.round(np.abs(Eff[:2,:2]), 4)}")
    return sir

check_interference(H_true, W_ideal, "IDEAL: H * W_ideal")
check_interference(H_true, W_est, "REAL: H * W_est")


# ==============================================================================
# Пункт 5: Моделирование SER vs SNR
# ==============================================================================
print("\n--- 5. Моделирование SER для выбранного пользователя ---")

target_user_idx = 0 

snr_range = range(0, 13)
ser_list = []
num_bits = 10**4

bits = np.random.randint(0, 2, num_bits)
syms = (1/np.sqrt(2)) * ((2*bits[::2]-1) + 1j*(2*bits[1::2]-1))

len_syms = len(syms)
x_streams = np.zeros((4, len_syms), dtype=complex)
x_streams[target_user_idx, :] = syms
for u in range(4):
    if u != target_user_idx:
        b_noise = np.random.randint(0, 2, num_bits)
        x_streams[u, :] = (1/np.sqrt(2)) * ((2*b_noise[::2]-1) + 1j*(2*b_noise[1::2]-1))

Tx_signal = W_est @ x_streams

Rx_signal_clean = H_true @ Tx_signal

Rx_user_clean = Rx_signal_clean[target_user_idx, :]
effective_channel_gain = (H_true @ W_est)[target_user_idx, target_user_idx]

for snr in snr_range:
    rx_noisy, _ = add_noise_to_signal(Rx_user_clean, snr)
    
    rx_eq = rx_noisy / effective_channel_gain
    
    ser = calculate_ser(rx_eq, syms)
    ser_list.append(ser)

plt.figure(figsize=(8, 6))
plt.semilogy(snr_range, ser_list, 'o-', linewidth=2, color='red', label=f'User {target_user_idx+1} SER')
plt.title(f"SER vs SNR для пользователя {target_user_idx+1}\n(MU-MIMO ZF c LS-оценкой канала)")
plt.xlabel("SNR, дБ")
plt.ylabel("Symbol Error Rate")
plt.grid(True, which='both', linestyle='--')
plt.legend()
plt.show()

print("Задание полностью выполнено.")