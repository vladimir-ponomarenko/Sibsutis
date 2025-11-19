import numpy as np
import matplotlib.pyplot as plt


N_bits = 10000  # Количество бит
channel_loss_dB = 40  # Потери в канале, дБ
d_lambda_ratio = 0.5  # Отношение расстояния между элементами к длине волны
theta_deg = 30  # Угол прихода сигнала, градусы

def get_steering_vector(N, theta_deg, d_lambda_ratio=0.5):
    """Вычисляет управляющий вектор для линейной АР."""
    theta_rad = np.deg2rad(theta_deg)
    n = np.arange(N)
    return np.exp(-1j * 2 * np.pi * d_lambda_ratio * n * np.sin(theta_rad))

def bpsk_qpsk_modulate(bits, modulation_type='BPSK'):
    """Модулирует биты в BPSK или QPSK."""
    if modulation_type == 'BPSK':
        return 2 * bits - 1
    elif modulation_type == 'QPSK':
        I = 2 * bits[0::2] - 1
        Q = 2 * bits[1::2] - 1
        return (I + 1j * Q) / np.sqrt(2)
    else:
        raise ValueError("Поддерживаются только 'BPSK' и 'QPSK'")

def calculate_ser(received_symbols, transmitted_symbols, modulation_type='BPSK'):
    """Вычисляет SER."""
    if modulation_type == 'BPSK':
        demodulated_bits = (np.real(received_symbols) > 0).astype(int)
        transmitted_bits = (np.real(transmitted_symbols) > 0).astype(int)
        return np.sum(demodulated_bits != transmitted_bits) / len(transmitted_bits)
    elif modulation_type == 'QPSK':
        demod_I = (np.real(received_symbols) > 0).astype(int)
        demod_Q = (np.imag(received_symbols) > 0).astype(int)
        orig_I = (np.real(transmitted_symbols) > 0).astype(int)
        orig_Q = (np.imag(transmitted_symbols) > 0).astype(int)
        symbol_errors = np.sum((demod_I != orig_I) | (demod_Q != orig_Q))
        return symbol_errors / len(transmitted_symbols)


def run_simulation(N_elements, modulation='QPSK'):
    print(f"\n--- Моделирование для N = {N_elements} элементов, модуляция {modulation} ---")

    # 1. Численно определить направленный вектор
    a = get_steering_vector(N_elements, theta_deg, d_lambda_ratio)
    print(f"1. Управляющий вектор (N={N_elements}):", np.round(a, 3))

    # 2. Сформировать блок передаваемых бит и модулированный сигнал
    bits = np.random.randint(0, 2, N_bits)
    tx_symbols = bpsk_qpsk_modulate(bits, modulation)
    print(f"2. Сформировано {len(tx_symbols)} символов {modulation}.")

    # 3. Вычислить принятые символы на АР
    channel_loss_linear = 10**(-channel_loss_dB / 20)
    h = channel_loss_linear * a
    received_signal_matrix = np.outer(h, tx_symbols)
    print("3. Принятые сигналы на АР вычислены.")

    # 4. Сформировать нормальный шум и сложить с принятыми сигналами (SNR=10 дБ)
    snr_db = 10
    snr_linear = 10**(snr_db / 10)
    signal_power = np.mean(np.abs(received_signal_matrix)**2)
    noise_power = signal_power / snr_linear
    noise = np.sqrt(noise_power / 2) * (np.random.randn(*received_signal_matrix.shape) + 1j * np.random.randn(*received_signal_matrix.shape))
    received_noisy_signal = received_signal_matrix + noise
    print(f"4. Добавлен шум для SNR = {snr_db} дБ.")

    # 5. Вычислить оптимальный весовой вектор
    w = np.conj(h)
    print("5. Оптимальный весовой вектор вычислен.")

    # 6. Применить весовой вектор и изобразить сигнальную диаграмму
    combined_signal = np.dot(w.T, received_noisy_signal)
    plt.figure(figsize=(12, 5))
    plt.suptitle(f"Сигнальные диаграммы для N={N_elements}, SNR={snr_db} дБ, {modulation}")
    plt.subplot(1, 2, 1)
    plt.scatter(np.real(received_noisy_signal[0, :]), np.imag(received_noisy_signal[0, :]), alpha=0.5)
    plt.title("На одном элементе АР")
    plt.grid(True); plt.axis('equal')
    plt.subplot(1, 2, 2)
    combined_signal_normalized = combined_signal / np.sqrt(np.mean(np.abs(combined_signal)**2))
    plt.scatter(np.real(combined_signal_normalized), np.imag(combined_signal_normalized), alpha=0.5)
    plt.title("На выходе схемы сложения (MRC)")
    plt.grid(True); plt.axis('equal')
    plt.show()
    print("6. Сигнальные диаграммы построены.")

    # 7. Моделирование для диапазона SNR и определение выигрыша
    snr_range_db = np.arange(0, 13, 1)
    ser_single_antenna = []
    ser_mrc = []

    for snr_db_iter in snr_range_db:
        snr_linear_iter = 10**(snr_db_iter / 10)
        noise_power_iter = signal_power / snr_linear_iter
        noise_iter = np.sqrt(noise_power_iter / 2) * (np.random.randn(*received_signal_matrix.shape) + 1j * np.random.randn(*received_signal_matrix.shape))
        received_noisy_iter = received_signal_matrix + noise_iter
        ser_single_antenna.append(calculate_ser(received_noisy_iter[0, :], tx_symbols, modulation))
        combined_signal_iter = np.dot(w.T, received_noisy_iter)
        ser_mrc.append(calculate_ser(combined_signal_iter, tx_symbols * np.dot(w.T, h), modulation))

    plt.figure(figsize=(8, 6))
    plt.semilogy(snr_range_db, ser_single_antenna, 'o-', label=f'Одна антенна')
    plt.semilogy(snr_range_db, ser_mrc, 's-', label=f'АР с MRC (N={N_elements})')
    plt.grid(True, which='both')
    plt.xlabel("Отношение сигнал/шум (SNR), дБ")
    plt.ylabel("Вероятность символьной ошибки (SER)")
    plt.title(f"Графики P=f(SNR) для {modulation}")
    plt.legend(); plt.ylim(1e-5, 1)
    plt.show()

    target_ser = 1e-2
    try:
        snr_fine = np.linspace(snr_range_db[0], snr_range_db[-1], 200)
        ser_single_fine = np.interp(snr_fine, snr_range_db, ser_single_antenna)
        ser_mrc_fine = np.interp(snr_fine, snr_range_db, ser_mrc)

        snr_single = np.interp(target_ser, ser_single_fine[::-1], snr_fine[::-1])
        snr_array = np.interp(target_ser, ser_mrc_fine[::-1], snr_fine[::-1])
        array_gain = snr_single - snr_array
        print(f"7. Выигрыш антенной решетки при SER={target_ser}: {array_gain:.2f} дБ")
    except Exception as e:
        print(f"7. Не удалось вычислить выигрыш: {e}")

run_simulation(N_elements=4, modulation='QPSK')
run_simulation(N_elements=8, modulation='QPSK')