import os
os.environ['QT_QPA_PLATFORM'] = 'xcb'

import numpy as np
import matplotlib
matplotlib.use('Qt5Agg')
import matplotlib.pyplot as plt
from scipy import interpolate

# Параметры системы
K = 64  # Количество поднесущих
CP = 16  # Длина циклического префикса
P = 12   # Количество пилотных поднесущих
pilotValue = 1 + 1j
allCarriers = np.arange(K)
pilotCarriers = allCarriers[::K//P]
pilotCarriers = np.hstack([pilotCarriers, np.array([allCarriers[-1]])])
P = P + 1
dataCarriers = np.delete(allCarriers, pilotCarriers)
mu = 2  # Биты на символ (QPSK)
#SNRdb = 25  # Отношение сигнал/шум в дБ
num_symbols = 20  # Количество OFDM символов для передачи
num_runs_per_snr = 1000
SNRdb_for_detailed_plots = 26

OFDM_TX_saved = None
y_comp_saved = None
symbol_starts_saved = None
cc_all_saved = None
payloadBits_saved = None
channelResponse_saved = None

SNR_dBs = np.arange(0, 31, 2)
BERs = []

# np.random.seed(42)

mapping_table = {
    (0, 0): 1 + 1j,
    (0, 1): 1 - 1j,
    (1, 0): -1 + 1j,
    (1, 1): -1 - 1j
}
demapping_table = {v: k for k, v in mapping_table.items()}

def SP(bits):
    """Распределение битов по символам"""
    return bits.reshape((len(dataCarriers), mu))

def Mapping(bits):
    """Отображение битов в символы QPSK"""
    return np.array([mapping_table[tuple(b)] for b in bits])

def OFDM_symbol(QAM_payload):
    """Размещение данных и пилотных символов"""
    symbol = np.zeros(K, dtype=complex)
    symbol[pilotCarriers] = pilotValue
    symbol[dataCarriers] = QAM_payload
    return symbol

def IDFT(OFDM_data):
    """Обратное дискретное преобразование Фурье"""
    return np.fft.ifft(OFDM_data)

def addCP(OFDM_time):
    """Добавление циклического префикса"""
    cp = OFDM_time[-CP:]
    return np.hstack([cp, OFDM_time])

def channel(signal, channelResponse, SNRdb, epsilon=0):
    """Моделирование канала с многолучевым затуханием, CFO и AWGN"""
    convolved = np.convolve(signal, channelResponse)

    n = np.arange(len(convolved))
    convolved = convolved * np.exp(1j * 2 * np.pi * epsilon * n / K)

    signal_power = np.mean(np.abs(signal)**2)
    sigma2 = signal_power * 10**(-SNRdb / 10)
    noise = np.sqrt(sigma2 / 2) * (np.random.randn(*convolved.shape) + 1j * np.random.randn(*convolved.shape))

    return convolved + noise

def symbol_sync(y, N, N_g, symbol_length, num_symbols):
    """Синхронизация символов OFDM"""
    len_y = len(y)
    symbol_starts = []
    cc_all = []
    d_max_all = []

    expected_positions = []
    for i in range(num_symbols):
        expected_pos = i * symbol_length
        expected_positions.append(expected_pos)

    search_window = CP * 2
    threshold = 0.65

    for expected_pos in expected_positions:
        start_pos = max(0, expected_pos - search_window)
        end_pos = min(len_y - N - N_g, expected_pos + search_window)

        if end_pos <= start_pos:
            continue

        cc = np.zeros(end_pos - start_pos, dtype=float)

        for d in range(start_pos, end_pos):
            if d + N + N_g >= len_y:
                continue

            W1 = y[d:d + N_g]
            W2 = y[d + N:d + N + N_g]
            C = np.sum(W1 * np.conj(W2))
            E1 = np.sum(np.abs(W1)**2)
            E2 = np.sum(np.abs(W2)**2)
            cc_index = d - start_pos
            cc[cc_index] = np.abs(C) / np.sqrt(E1 * E2) if E1 * E2 > 0 else 0

        if len(cc) > 0:
            max_index = np.argmax(cc)
            max_value = cc[max_index]

            if max_value > threshold:
                d_max = start_pos + max_index
                symbol_start = d_max + N_g

                is_duplicate = False
                for existing_start in symbol_starts:
                    if abs(symbol_start - existing_start) < N_g:
                        is_duplicate = True
                        break

                if not is_duplicate:
                    symbol_starts.append(symbol_start)
                    d_max_all.append(d_max)
                    cc_all.append(cc)

    if len(symbol_starts) < num_symbols:
        if len(symbol_starts) >= 2:
            intervals = [symbol_starts[i+1] - symbol_starts[i] for i in range(len(symbol_starts)-1)]
            mean_interval = int(np.mean(intervals))

            base_start = symbol_starts[0]
            existing_starts = set(symbol_starts)

            for i in range(num_symbols):
                estimated_pos = base_start + i * mean_interval
                estimated_d_max = estimated_pos - N_g

                if all(abs(estimated_pos - existing) > N_g for existing in existing_starts):
                    symbol_starts.append(estimated_pos)
                    d_max_all.append(estimated_d_max)
                    dummy_cc = np.zeros(N_g * 2)
                    dummy_cc[N_g] = 0.6
                    cc_all.append(dummy_cc)

            combined = list(zip(symbol_starts, d_max_all, cc_all))
            combined.sort(key=lambda x: x[0])
            symbol_starts = [item[0] for item in combined]
            d_max_all = [item[1] for item in combined]
            cc_all = [item[2] for item in combined]

            symbol_starts = symbol_starts[:num_symbols]
            d_max_all = d_max_all[:num_symbols]
            cc_all = cc_all[:num_symbols]

    return symbol_starts, cc_all, d_max_all

def estimate_CFO(y, d_max, N, N_g):
    """Оценка смещения частоты несущей (CFO)"""
    W1 = y[d_max:d_max + N_g]
    W2 = y[d_max + N:d_max + N + N_g]
    sum_val = np.sum(np.conj(W1) * W2)
    epsilon = (1 / (2 * np.pi)) * np.angle(sum_val)
    return epsilon

def compensate_CFO(y, epsilon, N):
    """Компенсация смещения частоты несущей"""
    n = np.arange(len(y))
    return y * np.exp(-1j * 2 * np.pi * epsilon * n / N)

def removeCP(signal, symbol_start, N):
    """Удаление циклического префикса"""
    return signal[symbol_start:symbol_start + N]

def DFT(OFDM_RX):
    """Дискретное преобразование Фурье"""
    return np.fft.fft(OFDM_RX)

def channelEstimate(OFDM_demod, pilotCarriers, pilotValue):
    """Оценка канала с использованием пилотных поднесущих"""
    pilots = OFDM_demod[pilotCarriers]
    Hest_at_pilots = pilots / pilotValue
    Hest_abs = interpolate.interp1d(pilotCarriers, np.abs(Hest_at_pilots), kind='linear')(allCarriers)
    Hest_phase = interpolate.interp1d(pilotCarriers, np.angle(Hest_at_pilots), kind='linear')(allCarriers)

    return Hest_abs * np.exp(1j * Hest_phase)

def equalize(OFDM_demod, Hest):
    """Эквализация частотной области"""
    return OFDM_demod / Hest

def get_payload(equalized):
    """Извлечение данных из эквализированного сигнала"""
    return equalized[dataCarriers]

def Demapping(QAM):
    """Обратное отображение символов QPSK в биты"""
    constellation = np.array([x for x in demapping_table.keys()])
    dists = np.abs(QAM.reshape((-1, 1)) - constellation.reshape((1, -1)))
    const_index = dists.argmin(axis=1)
    hardDecision = constellation[const_index]
    return np.vstack([demapping_table[C] for C in hardDecision]), hardDecision

for SNRdb in SNR_dBs:
    ber_for_current_snr = []
    print(f"\n--- Симуляция для SNR = {SNRdb} дБ ---")

    for run in range(num_runs_per_snr):
        print(f"  Запуск {run + 1}/{num_runs_per_snr}...")

        payloadBits_per_symbol = len(dataCarriers) * mu
        payloadBits = np.random.binomial(n=1, p=0.5, size=(num_symbols, payloadBits_per_symbol))
        OFDM_TX_symbols = []

        for i in range(num_symbols):
            bits = payloadBits[i]
            bits_SP = SP(bits)
            QAM = Mapping(bits_SP)
            OFDM_data = OFDM_symbol(QAM)
            OFDM_time = IDFT(OFDM_data)
            OFDM_withCP = addCP(OFDM_time)
            OFDM_TX_symbols.append(OFDM_withCP)

        OFDM_TX = np.hstack(OFDM_TX_symbols)

        channelResponse = np.array([1, 0, 0.3 + 0.3j])
        epsilon_true = 0.1
        OFDM_RX = channel(OFDM_TX, channelResponse, SNRdb, epsilon_true)

        symbol_length = K + CP
        symbol_starts, cc_all, d_max_all = symbol_sync(OFDM_RX, K, CP, symbol_length, num_symbols)

        y_comp = None
        if len(symbol_starts) > 0:
            epsilon_est = estimate_CFO(OFDM_RX, d_max_all[0], K, CP)
            y_comp = compensate_CFO(OFDM_RX, epsilon_est, K)

            bits_est_all = []
            for i, start in enumerate(symbol_starts):
                if start + K > len(y_comp): continue
                y_symbol = removeCP(y_comp, start, K)
                Y = DFT(y_symbol)
                Hest = channelEstimate(Y, pilotCarriers, pilotValue)
                equalized = equalize(Y, Hest)
                QAM_est = get_payload(equalized)
                bits_est, _ = Demapping(QAM_est)
                bits_est_all.append(bits_est.reshape((-1,)))

            if bits_est_all:
                bits_est_all = np.hstack(bits_est_all)
                min_len = min(len(bits_est_all), len(payloadBits.flatten()))
                BER = np.sum(np.abs(payloadBits.flatten()[:min_len] - bits_est_all[:min_len])) / min_len
                ber_for_current_snr.append(BER)
            else:
                ber_for_current_snr.append(1.0)
        else:
            ber_for_current_snr.append(1.0)

        if SNRdb == SNRdb_for_detailed_plots:
            OFDM_TX_saved = OFDM_TX
            y_comp_saved = y_comp
            symbol_starts_saved = symbol_starts
            cc_all_saved = cc_all
            payloadBits_saved = payloadBits
            channelResponse_saved = channelResponse

    average_ber = np.mean(ber_for_current_snr)
    print(f"--> Средний BER для SNR = {SNRdb} дБ: {average_ber:.7f}")
    BERs.append(average_ber)


plt.figure(figsize=(10, 7))
plt.semilogy(SNR_dBs, BERs, marker='o', linestyle='-')
plt.title('BER от SNR')
plt.xlabel('SNR, дБ')
plt.ylabel('BER')
plt.grid(True, which="both", ls="--")
plt.ylim(bottom=1e-5, top=1.1)
plt.show()

if OFDM_TX_saved is not None:
    fig, axes = plt.subplots(3, 2, figsize=(14, 14))
    fig.suptitle(f'Графики для SNR = {SNRdb_for_detailed_plots} дБ', fontsize=16)

    cc_concat = np.concatenate(cc_all_saved) if cc_all_saved else np.array([])
    axes[0, 0].plot(cc_concat, label='Кросс-корреляция')
    axes[0, 0].set_title('Кросс-корреляция для синхронизации')
    axes[0, 0].grid(True)

    axes[0, 1].plot(np.real(OFDM_TX_saved), label='Вещественная часть')
    axes[0, 1].plot(np.imag(OFDM_TX_saved), label='Мнимая часть', linestyle='--')
    if symbol_starts_saved:
        for start in symbol_starts_saved[:5]:
            axes[0, 1].axvline(x=start, color='r', linestyle='--')
    axes[0, 1].set_title('OFDM-сигнал с CP (временная область)')
    axes[0, 1].legend()
    axes[0, 1].grid(True)

    for i in range(num_symbols):
        OFDM_data = OFDM_symbol(Mapping(SP(payloadBits_saved[i])))
        axes[1, 0].stem(allCarriers + i * 2, np.abs(OFDM_data), label=f'Символ {i+1}')
    axes[1, 0].set_title('OFDM-сигнал (частотная область)')
    axes[1, 0].set_xlabel("Номер поднесущей")
    axes[1, 0].set_ylabel("Амплитуда")
    axes[1, 0].grid(True)
    axes[1, 0].legend()

    if y_comp_saved is not None and len(symbol_starts_saved) > 0:
        all_Y_values = []
        for i, start in enumerate(symbol_starts_saved[:5]):
            if start + K > len(y_comp_saved): continue
            y_symbol = removeCP(y_comp_saved, start, K)
            Y = DFT(y_symbol)
            all_Y_values.append(Y[dataCarriers])
        if all_Y_values:
            axes[1, 1].scatter(np.concatenate(all_Y_values).real, np.concatenate(all_Y_values).imag, c='blue', alpha=0.5, s=10)
        axes[1, 1].set_title('Созвездие до эквализации')
        axes[1, 1].grid(True)
        axes[1, 1].axis('equal')
    else:
        axes[1, 1].text(0.5, 0.5, 'Данные недоступны', ha='center', va='center')
        axes[1, 1].axis('off')

    if y_comp_saved is not None and len(symbol_starts_saved) > 0:
        H_exact = np.fft.fft(channelResponse_saved, K)
        for i, start in enumerate(symbol_starts_saved[:5]):
            if start + K > len(y_comp_saved): continue
            y_symbol = removeCP(y_comp_saved, start, K)
            Y = DFT(y_symbol)
            Hest = channelEstimate(Y, pilotCarriers, pilotValue)
            axes[2, 0].plot(allCarriers, np.abs(Hest), label=f'Символ {i+1}')
        axes[2, 0].plot(allCarriers, np.abs(H_exact), 'k--', label='Истинный канал')
        axes[2, 0].set_title('Оценка канала')
        axes[2, 0].legend()
        axes[2, 0].grid(True)
    else:
        axes[2, 0].text(0.5, 0.5, 'Данные недоступны', ha='center', va='center')
        axes[2, 0].axis('off')

    if y_comp_saved is not None and len(symbol_starts_saved) > 0:
        constellation_points = np.array(list(mapping_table.values()))
        axes[2, 1].scatter(constellation_points.real, constellation_points.imag, c='red', marker='*', s=100, label='Референсные точки')
        all_QAM_est = []
        for i, start in enumerate(symbol_starts_saved[:5]):
            if start + K > len(y_comp_saved): continue
            y_symbol = removeCP(y_comp_saved, start, K)
            Y = DFT(y_symbol)
            Hest = channelEstimate(Y, pilotCarriers, pilotValue)
            equalized = equalize(Y, Hest)
            all_QAM_est.append(get_payload(equalized))
        if all_QAM_est:
            axes[2, 1].scatter(np.concatenate(all_QAM_est).real, np.concatenate(all_QAM_est).imag, c='blue', alpha=0.5, s=10, label='Принятые символы')
        axes[2, 1].set_title('Созвездие после эквализации')
        axes[2, 1].grid(True)
        axes[2, 1].axis('equal')
        axes[2, 1].legend()
    else:
        axes[2, 1].text(0.5, 0.5, 'Данные недоступны', ha='center', va='center')
        axes[2, 1].axis('off')

    plt.tight_layout(rect=[0, 0, 1, 0.96])
    plt.show()
else:
    print(f"\nВнимание: Данные для графиков при SNR = {SNRdb_for_detailed_plots} дБ не были найдены.")
    print(f"Убедитесь, что выбранное значение присутствует в списке SNR_dBs: {SNR_dBs}")