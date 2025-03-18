import matplotlib.pyplot as plt
import numpy as np
import scipy.signal

fs = 30e3
N = 1000
num_realizations = 1000

def create_filters():
    N_low = 6
    Rp_low = 0.5
    Rs_low = 50
    Wn_low = 3e3 / (fs / 2)
    b_low, a_low = scipy.signal.ellip(N_low, Rp_low, Rs_low, Wn_low, btype='low', analog=False)
    
    N_band = 6
    Rp_band = 0.5
    Rs_band = 50
    Wn_band = [3e3/(fs/2), 6e3/(fs/2)]
    b_band, a_band = scipy.signal.ellip(N_band, Rp_band, Rs_band, Wn_band, btype='band', analog=False)
    
    return (b_low, a_low), (b_band, a_band)

(b_low, a_low), (b_band, a_band) = create_filters()

white_noise = np.random.normal(0, 1, N)

acf_input = np.correlate(white_noise, white_noise, mode='full')[N-1:]

fft_input = np.fft.fft(white_noise)
psd_input = np.abs(fft_input)**2

def process_realizations(b, a):
    acf_list = []
    psd_list = []
    for _ in range(num_realizations):
        noise = np.random.normal(0, 1, N)
        filtered = scipy.signal.lfilter(b, a, noise)
        acf = np.correlate(filtered, filtered, mode='full')[N-1:]
        acf_list.append(acf)
        fft = np.fft.fft(filtered)
        psd = np.abs(fft)**2
        psd_list.append(psd)
    avg_acf = np.mean(acf_list, axis=0)
    avg_psd = np.mean(psd_list, axis=0)
    return avg_acf, avg_psd

acf_low, psd_low = process_realizations(b_low, a_low)

acf_band, psd_band = process_realizations(b_band, a_band)

max_acf = np.max(acf_low)
threshold = max_acf / np.exp(1)
indices = np.where(acf_low >= threshold)[0]
correlation_interval = indices[-1] - indices[0]
print(f"Интервал корреляции ФНЧ: {correlation_interval} отсчетов")

b_up = [1]
a_up = [1, -0.9]

def process_up_realizations():
    acf_list = []
    psd_list = []
    for _ in range(num_realizations):
        noise = np.random.normal(0, 1, N)
        filtered = scipy.signal.lfilter(b_up, a_up, noise)
        acf = np.correlate(filtered, filtered, mode='full')[N-1:]
        acf_list.append(acf)
        fft = np.fft.fft(filtered)
        psd = np.abs(fft)**2
        psd_list.append(psd)
    avg_acf = np.mean(acf_list, axis=0)
    avg_psd = np.mean(psd_list, axis=0)
    return avg_acf, avg_psd

acf_up, psd_up = process_up_realizations()

plt.figure(figsize=(16, 12))

plt.subplot(3, 2, 1)
plt.plot(acf_input)
plt.title('АКФ входного белого шума')
plt.xlabel('Отсчеты')
plt.ylabel('АКФ')

plt.subplot(3, 2, 2)
frequencies = np.fft.rfftfreq(N, d=1/fs)
plt.plot(frequencies, psd_input[:len(frequencies)])
plt.title('СПМ входного белого шума')
plt.xlabel('Частота (Гц)')
plt.ylabel('СПМ')

plt.subplot(3, 2, 3)
plt.plot(acf_low)
plt.title('АКФ ФНЧ (усреднение 1000 реализаций)')
plt.xlabel('Отсчеты')
plt.ylabel('АКФ')

plt.subplot(3, 2, 4)
plt.plot(frequencies, psd_low[:len(frequencies)])
plt.title('СПМ ФНЧ (усреднение 1000 реализаций)')
plt.xlabel('Частота (Гц)')
plt.ylabel('СПМ')

plt.subplot(3, 2, 5)
plt.plot(acf_band)
plt.title('АКФ ПФ (усреднение 1000 реализаций)')
plt.xlabel('Отсчеты')
plt.ylabel('АКФ')

plt.subplot(3, 2, 6)
plt.plot(frequencies, psd_band[:len(frequencies)])
plt.title('СПМ ПФ (усреднение 1000 реализаций)')
plt.xlabel('Частота (Гц)')
plt.ylabel('СПМ')

plt.tight_layout()
plt.show()

plt.figure(figsize=(10, 6))

plt.subplot(2, 1, 1)
plt.plot(acf_up)
plt.title('АКФ УП СП')
plt.xlabel('Отсчеты')
plt.ylabel('АКФ')

plt.subplot(2, 1, 2)
plt.plot(frequencies, psd_up[:len(frequencies)])
plt.title('СПМ УП СП')
plt.xlabel('Частота (Гц)')
plt.ylabel('СПМ')

plt.tight_layout()
plt.show()