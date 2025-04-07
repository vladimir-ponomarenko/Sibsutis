import numpy as np
import matplotlib.pyplot as plt

bits = np.array([1, 0, 1, 1, 0, 0])
samples_per_bit = 8  
snr_db = 10          

print(f"Исходные биты: {bits}")

signal_level = 2 * bits - 1
print(f"Уровни сигнала для бит: {signal_level}")

signal = np.repeat(signal_level, samples_per_bit)
time = np.arange(len(signal))

signal_power = np.mean(signal**2) 

snr_linear = 10**(snr_db / 10.0)
noise_power = signal_power / snr_linear

noise_sigma = np.sqrt(noise_power)

noise = noise_sigma * np.random.randn(len(signal))

print(f"\nПараметры шума:")
print(f"  SNR = {snr_db} дБ")
print(f"  Мощность сигнала = {signal_power:.2f}")
print(f"  Расчетная мощность шума = {noise_power:.4f}")
print(f"  Стандартное отклонение шума (sigma) = {noise_sigma:.4f}")
print(f"  Фактическая мощность сгенерированного шума = {np.mean(noise**2):.4f}") 


noisy_signal = signal + noise



template = np.ones(samples_per_bit)

correlation = np.correlate(noisy_signal, template, mode='valid')

correlation_time = np.arange(len(correlation))

sampling_points_indices = np.arange(0, len(correlation), samples_per_bit)

valid_sampling_points = sampling_points_indices[sampling_points_indices < len(correlation)]
decision_values = correlation[valid_sampling_points]
received_bits = (decision_values > 0).astype(int)

print("\n--- Результаты приема ---")
print(f"Значения корреляции в точках решения: {decision_values}")
print(f"Исходные биты:    {bits}")
print(f"Принятые биты:    {received_bits}")
num_errors = np.sum(bits != received_bits)
print(f"Количество ошибочных бит: {num_errors} из {len(bits)}")
ber = num_errors / len(bits) if len(bits) > 0 else 0
print(f"BER (Bit Error Rate): {ber:.2f}")





fig, axs = plt.subplots(3, 1, figsize=(10, 9), sharex=False) 


axs[0].plot(time, signal, drawstyle='steps-post')
axs[0].set_title('Исходный передаваемый сигнал (без шума)')
axs[0].set_ylabel('Амплитуда')
axs[0].set_yticks([-1, 0, 1])
axs[0].grid(True)
axs[0].set_ylim(-1.5, 1.5)




axs[1].plot(time, noisy_signal, label=f'Сигнал с шумом (SNR={snr_db} дБ)')

axs[1].plot(time, signal, drawstyle='steps-post', linestyle='--', alpha=0.5, label='Исходный сигнал')
axs[1].set_title(f'Сигнал с добавленным шумом (SNR = {snr_db} дБ)')
axs[1].set_xlabel('Отсчеты')
axs[1].set_ylabel('Амплитуда')
axs[1].grid(True)
axs[1].legend(loc='upper right')


axs[2].plot(correlation_time, correlation, label='Выход коррелятора')
axs[2].plot(valid_sampling_points, correlation[valid_sampling_points], 'ro', markersize=8, label='Точки принятия решения')
axs[2].set_title('Выход коррелятора (согласованного фильтра)')
axs[2].set_xlabel('Начальный отсчет окна корреляции')
axs[2].set_ylabel('Значение корреляции')
axs[2].grid(True)
axs[2].legend(loc='upper right')


plt.tight_layout()


plt.show()