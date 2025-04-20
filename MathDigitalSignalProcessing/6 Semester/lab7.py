import numpy as np
import matplotlib.pyplot as plt
from scipy.special import erfc
from scipy.signal import correlate 

################################
# Тестовый вариант лабораторной#
################################

num_symbols = 10000  
n_cycles_per_symbol = 5
fc = 1000
sps = 100

Ts = n_cycles_per_symbol / fc
fs = sps / Ts
dt = 1 / fs
t_symbol = np.linspace(0, Ts, sps, endpoint=False)

snr_db_range = np.arange(0, 16, 2) 


tx_symbols = np.random.randint(0, 2, num_symbols)


A = 1.0
s1_base = A * np.cos(2 * np.pi * fc * t_symbol)
s0_ask_base = np.zeros(sps)
s0_psk_base = A * np.cos(2 * np.pi * fc * t_symbol + np.pi)


tx_signal_ask = np.zeros(num_symbols * sps)
tx_signal_psk = np.zeros(num_symbols * sps)
for i in range(num_symbols):
    start_idx = i * sps
    end_idx = (i + 1) * sps
    if tx_symbols[i] == 1:
        tx_signal_ask[start_idx:end_idx] = s1_base
        tx_signal_psk[start_idx:end_idx] = s1_base
    else:
        tx_signal_ask[start_idx:end_idx] = s0_ask_base
        tx_signal_psk[start_idx:end_idx] = s0_psk_base


ber_ask_sim = []
ber_psk_sim = []
ber_ask_theo = []
ber_psk_theo = []

def Q_func(x):
    return 0.5 * erfc(x / np.sqrt(2))

E1_ask_sum_sq = np.sum(s1_base**2)
Vt_ask = E1_ask_sum_sq / 2
Vt_psk = 0

for snr_db in snr_db_range:
    
    snr_lin = 10**(snr_db / 10)

    
    sig_power_ask = np.mean(tx_signal_ask**2)
    noise_power_ask = sig_power_ask / snr_lin if snr_lin > 0 else np.inf
    noise_ask = np.random.normal(0, np.sqrt(noise_power_ask), len(tx_signal_ask)) if snr_lin > 0 else 0
    rx_signal_ask = tx_signal_ask + noise_ask

    
    rx_symbols_ask = np.zeros(num_symbols, dtype=int)
    errors_ask = 0
    for i in range(num_symbols):
        symbol_waveform_ask = rx_signal_ask[i*sps:(i+1)*sps]
        corr_ask = np.sum(symbol_waveform_ask * s1_base)
        rx_symbols_ask[i] = 1 if corr_ask > Vt_ask else 0
        if rx_symbols_ask[i] != tx_symbols[i]: errors_ask += 1

    
    ber_ask = errors_ask / num_symbols
    ber_ask_sim.append(ber_ask if ber_ask > 0 else 1e-9)

    
    sig_power_psk = np.mean(tx_signal_psk**2)
    noise_power_psk = sig_power_psk / snr_lin if snr_lin > 0 else np.inf
    noise_psk = np.random.normal(0, np.sqrt(noise_power_psk), len(tx_signal_psk)) if snr_lin > 0 else 0
    rx_signal_psk = tx_signal_psk + noise_psk

    
    rx_symbols_psk = np.zeros(num_symbols, dtype=int)
    errors_psk = 0
    for i in range(num_symbols):
        symbol_waveform_psk = rx_signal_psk[i*sps:(i+1)*sps]
        corr_psk = np.sum(symbol_waveform_psk * s1_base)
        rx_symbols_psk[i] = 1 if corr_psk > Vt_psk else 0
        if rx_symbols_psk[i] != tx_symbols[i]: errors_psk += 1

    
    ber_psk = errors_psk / num_symbols
    ber_psk_sim.append(ber_psk if ber_psk > 0 else 1e-9)

    
    gamma_s_ask = sig_power_ask / noise_power_ask if noise_power_ask > 0 else np.inf
    ber_a_t = Q_func(np.sqrt(2 * gamma_s_ask))
    ber_ask_theo.append(ber_a_t if ber_a_t > 0 else 1e-9)

    gamma_s_psk = sig_power_psk / noise_power_psk if noise_power_psk > 0 else np.inf
    ber_p_t = Q_func(np.sqrt(gamma_s_psk)) 
    ber_psk_theo.append(ber_p_t if ber_p_t > 0 else 1e-9)


plt.figure(figsize=(10, 7))
plt.semilogy(snr_db_range, ber_ask_sim, 'bo-', label='ASK (ДАМ) - Моделирование')
plt.semilogy(snr_db_range, ber_ask_theo, 'b--', label='ASK (ДАМ) - Теория (Q(sqrt(2*gamma_s)))')
plt.semilogy(snr_db_range, ber_psk_sim, 'rs-', label='PSK (ДФМ) - Моделирование')
plt.semilogy(snr_db_range, ber_psk_theo, 'r--', label='PSK (ДФМ) - Теория (Q(sqrt(gamma_s)))')
plt.ylim(1e-5, 1.0)
plt.xlabel('Отношение сигнал/шум (SNR), дБ')
plt.ylabel('Вероятность битовой ошибки (BER)')
plt.title('ЛР1: Зависимость BER от SNR (Корреляционный приемник)')
plt.legend()
plt.grid(True, which='both', linestyle='--')


print("--- Лабораторное задание 1 завершено ---")
print("\n--- Лабораторное задание 2: Согласованный фильтр ---")






print("\n2. Связь ИХ СФ и сигнала (Коды Баркера)")


barker_5 = np.array([+1, +1, +1, -1, +1])
barker_7 = np.array([+1, +1, +1, -1, -1, +1, -1])
barker_11 = np.array([+1, -1, +1, +1, -1, +1, +1, +1, -1, -1, -1]) 

signal_s = barker_7
N = len(signal_s)
print(f"Выбранный сигнал (Баркер-{N}): {signal_s}")



impulse_response_h = signal_s[::-1]
print(f"Импульсная характеристика СФ h(n): {impulse_response_h}")


plt.figure(figsize=(10, 4))
plt.subplot(1, 2, 1)
plt.stem(np.arange(N), signal_s, basefmt="b-")
plt.title(f'Сигнал s(n) (Баркер-{N})')
plt.xlabel('n')
plt.ylabel('Амплитуда')
plt.grid(True)

plt.subplot(1, 2, 2)
plt.stem(np.arange(N), impulse_response_h, basefmt="r-")
plt.title('ИХ согл. фильтра h(n)=s(N-1-n)')
plt.xlabel('n')
plt.ylabel('Амплитуда')
plt.grid(True)
plt.tight_layout()



print("\n3. Форма сигнала на выходе СФ (Корреляция)")



signal_matched = signal_s           
signal_inverted = -signal_s         
signal_mismatched = np.array([+1, -1, +1, -1, +1, -1, +1]) 
if len(signal_mismatched) != N: signal_mismatched = np.sign(np.random.randn(N)) 



output_matched = np.correlate(signal_matched, signal_s, mode='full')
output_inverted = np.correlate(signal_inverted, signal_s, mode='full')
output_mismatched = np.correlate(signal_mismatched, signal_s, mode='full')




lags = np.arange(-(N - 1), N)


plt.figure(figsize=(10, 6))
plt.plot(lags, output_matched, 'bo-', label=f'Вход: Баркер-{N} (соглас.)')
plt.plot(lags, output_inverted, 'ro-', label=f'Вход: Инвертированный Баркер-{N}')
plt.plot(lags, output_mismatched, 'go-', label='Вход: Несогласованный')
plt.title('Сигнал на выходе согласованного фильтра (Корреляция входа с s(n))')
plt.xlabel('Сдвиг (m)')
plt.ylabel('Амплитуда выхода K(m)')
plt.legend()
plt.grid(True)


print(f"Макс. выход для согласованного сигнала: {np.max(output_matched)} (при m=0)")
print(f"Макс. выход для инвертированного сигнала: {np.min(output_inverted)} (при m=0)")
print(f"Макс. выход для несогласованного сигнала: {np.max(np.abs(output_mismatched))}")


print("\n4. Влияние искажения элементов")


signal_distorted_1 = signal_s.copy()
center_idx = N // 2
signal_distorted_1[center_idx] *= -1
print(f"Искаженный сигнал (1 элемент): {signal_distorted_1}")


signal_distorted_2 = signal_s.copy()
indices_to_flip = [1, N - 2] 
signal_distorted_2[indices_to_flip] *= -1
print(f"Искаженный сигнал (2 элемента): {signal_distorted_2}")


output_distorted_1 = np.correlate(signal_distorted_1, signal_s, mode='full')
output_distorted_2 = np.correlate(signal_distorted_2, signal_s, mode='full')


plt.figure(figsize=(10, 6))
plt.plot(lags, output_matched, 'b-', label='Выход: Исходный сигнал (без искаж.)')
plt.plot(lags, output_distorted_1, 'r--', label='Выход: Искажен 1 элемент')
plt.plot(lags, output_distorted_2, 'g:', label='Выход: Искажены 2 элемента')
plt.title('Влияние искажения элементов на выход СФ')
plt.xlabel('Сдвиг (m)')
plt.ylabel('Амплитуда выхода K(m)')
plt.legend()
plt.grid(True)


print(f"Макс. выход для искаж. (1): {output_distorted_1[N - 1]} (было {output_matched[N - 1]})")
print(f"Макс. выход для искаж. (2): {output_distorted_2[N - 1]} (было {output_matched[N - 1]})")


print("\n5. Влияние аддитивного шума")


snr_db_levels = [20, 10, 5, 0] 

plt.figure(figsize=(10, 6))
plt.plot(lags, output_matched, 'b-', label='Выход: Без шума', linewidth=2)


sig_power = np.mean(signal_s**2) 

for snr_db in snr_db_levels:
    snr_lin = 10**(snr_db / 10.0)
    
    noise_power = sig_power / snr_lin
    
    noise = np.random.normal(0, np.sqrt(noise_power), N)
    
    signal_noisy = signal_s + noise
    
    output_noisy = np.correlate(signal_noisy, signal_s, mode='full')
    
    plt.plot(lags, output_noisy, '--', label=f'Выход: SNR = {snr_db} дБ')

plt.title('Влияние аддитивного шума на выход СФ')
plt.xlabel('Сдвиг (m)')
plt.ylabel('Амплитуда выхода K(m)')
plt.legend()
plt.grid(True)



plt.show()