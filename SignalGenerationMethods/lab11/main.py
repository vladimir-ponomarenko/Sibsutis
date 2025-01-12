import numpy as np
import matplotlib.pyplot as plt

np.random.seed(42)

def get_steering_vector(N, theta_deg):
    """
    Формирует нормированный управляющий вектор.
    """
    theta_rad = np.deg2rad(theta_deg)
    n = np.arange(N)
    # d = lambda/2 -> фазовый сдвиг pi * sin(theta)
    vec = np.exp(-1j * np.pi * n * np.sin(theta_rad)) / np.sqrt(N)
    return vec

def qpsk_modulate(bits):
    """Модуляция QPSK."""
    symbols = []
    for i in range(0, len(bits), 2):
        b = bits[i:i+2]
        # 00->1+j, 01->-1+j, 11->-1-j, 10->1-j
        real = 1 if b[0] == 0 else -1
        imag = 1 if b[1] == 0 else -1
        symbols.append((real + 1j*imag)/np.sqrt(2))
    return np.array(symbols)

def detect_qpsk(received):
    """Демодуляция QPSK."""
    bits = []
    for s in received:
        r = 0 if s.real > 0 else 1
        i = 0 if s.imag > 0 else 1
        bits.extend([r, i])
    return np.array(bits)


print("=== Пункт 1: Направленные векторы и ортогональность ===")
Nt = 8

# k=0 (0 град) и k=1 (arcsin(2/8))
u1 = 0
u2 = 2/Nt
angle1 = np.degrees(np.arcsin(u1))
angle2 = np.degrees(np.arcsin(u2))

vec1 = get_steering_vector(Nt, angle1)
vec2 = get_steering_vector(Nt, angle2)

ortho_check = np.vdot(vec1, vec2)
print(f"Углы: {angle1:.2f}, {angle2:.2f}")
print(f"Скалярное произведение (модуль): {np.abs(ortho_check):.2e}")
if np.abs(ortho_check) < 1e-10:
    print("Результат: Условие ортогональности ВЫПОЛНЕНО.")
else:
    print("Результат: Условие ортогональности НЕ выполнено.")
print("-" * 20)


print("=== Пункт 2: Вычисление матрицы канала H ===")
Nr = 8
Np = 20
H = np.zeros((Nr, Nt), dtype=complex)

tx_angles = np.random.uniform(-30, 30, Np)
rx_angles = np.random.uniform(-60, 60, Np)
# Случайные комплексные амплитуды (затухания)
alphas = (np.random.randn(Np) + 1j * np.random.randn(Np)) / np.sqrt(2)

for l in range(Np):
    ar = get_steering_vector(Nr, rx_angles[l])
    at = get_steering_vector(Nt, tx_angles[l])
    # H = sum( alpha * ar * at^H )
    H += alphas[l] * np.outer(ar, at.conj())

print("Матрица H вычислена.")
print("-" * 20)


print("=== Пункт 3: SVD, ранг, оптимальные векторы ===")
# H = U * S * Vh
U, S, Vh = np.linalg.svd(H)
rank = np.linalg.matrix_rank(H)
max_sigma = S[0]


w_tx = Vh[0].conj()
w_rx = U[:, 0].conj()

print(f"Ранг канала: {rank}")
print(f"Макс. сингулярное число: {max_sigma:.4f}")
print("-" * 20)


print("=== Пункт 4: Формирование бит и модуляция ===")
num_bits = 10000
bits = np.random.randint(0, 2, num_bits)
symbols = qpsk_modulate(bits)
print(f"Сформировано {len(symbols)} символов QPSK.")
print("-" * 20)


print("=== Пункт 5: Векторы сигналов на передаче ===")
# x = w_tx * s (вектор столбец * строка символов)
X_tx = np.outer(w_tx, symbols)
print(f"Размер матрицы передаваемых сигналов: {X_tx.shape}")
print("-" * 20)


print("=== Пункт 6: Принятые символы и потери ===")
# r = H * x
R_clean = H @ X_tx

# Потери 40 дБ -> по мощности 10^-4, по амплитуде 10^-2
loss_scale = 10**(-40/20)
R_clean = R_clean * loss_scale
print("Потери распространения (40 дБ) учтены.")
print("-" * 20)


print("=== Пункт 7: Добавление шума (SNR = 10 дБ) ===")
target_snr_db = 10
sig_power = np.mean(np.abs(R_clean)**2)
# P_noise = P_sig / SNR
noise_power = sig_power / (10**(target_snr_db/10))
noise_std = np.sqrt(noise_power / 2)

noise = noise_std * (np.random.randn(*R_clean.shape) + 1j * np.random.randn(*R_clean.shape))
R_noisy = R_clean + noise
print(f"Шум добавлен для SNR = {target_snr_db} дБ")
print("-" * 20)


print("=== Пункт 8: Оптимальный весовой вектор схемы сложения ===")
print("Используется вектор w_rx из п.3.")
print("-" * 20)


print("=== Пункт 9: Применение весового вектора и диаграммы ===")
# z = w_rx^T * r.
Z_combined = w_rx.T @ R_noisy

One_element = R_noisy[0, :]

plt.figure(figsize=(12, 5))
plt.subplot(1, 2, 1)
plt.scatter(One_element.real, One_element.imag, alpha=0.5, s=2)
plt.title(f"Одна антенна (SNR ~ {target_snr_db} дБ)")
plt.grid(True)
plt.axis('equal')

plt.subplot(1, 2, 2)
plt.scatter(Z_combined.real, Z_combined.imag, alpha=0.5, s=2, color='red')
plt.title("Выход схемы сложения (MIMO)")
plt.grid(True)
plt.axis('equal')
plt.show()


print("=== Пункт 10: Моделирование BER vs SNR ===")
snr_range = np.arange(0, 13, 1)
ber_single = []
ber_mimo = []
h_siso_ref = (H @ w_tx)[0]

for snr in snr_range:
    current_noise_power = sig_power / (10**(snr/10))
    current_std = np.sqrt(current_noise_power / 2)

    noise_iter = current_std * (np.random.randn(*R_clean.shape) + 1j * np.random.randn(*R_clean.shape))
    R_iter = R_clean + noise_iter

    # --- 1. Прием на одну антенну (SISO) ---
    y_siso = R_iter[0, :]
    s_est_siso = y_siso / h_siso_ref
    bits_siso = detect_qpsk(s_est_siso)
    errors_siso = np.sum(bits != bits_siso)
    ber_single.append(errors_siso / num_bits)

    # --- 2. Прием на решетку (MIMO Beamforming) ---
    z_mimo = w_rx.T @ R_iter
    channel_gain_mimo = max_sigma * loss_scale
    s_est_mimo = z_mimo / channel_gain_mimo
    bits_mimo = detect_qpsk(s_est_mimo)
    errors_mimo = np.sum(bits != bits_mimo)
    ber_mimo.append(errors_mimo / num_bits)

plt.figure(figsize=(10, 6))
plt.semilogy(snr_range, ber_single, 'b-o', label='Одна антенна')
plt.semilogy(snr_range, ber_mimo, 'r-s', label=f'Решетка ({Nr} эл.)')
plt.xlabel('SNR (дБ)')
plt.ylabel('Вероятность ошибки (BER)')
plt.title('Вероятность ошибки P=f(SNR)')
plt.grid(True, which="both", ls='-')
plt.legend()
plt.show()

idx_target = np.abs(np.array(ber_mimo) - 1e-3).argmin()
