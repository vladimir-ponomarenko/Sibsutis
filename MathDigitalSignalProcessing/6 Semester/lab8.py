import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm

N = 10000
EbN0_db_range = np.arange(0, 11, 1)
bits = np.random.randint(0, 2, N)

ber_bpsk_simulated = np.zeros(len(EbN0_db_range))
ber_ask_simulated = np.zeros(len(EbN0_db_range))
ber_bpsk_theoretical = np.zeros(len(EbN0_db_range))
ber_ask_theoretical = np.zeros(len(EbN0_db_range))

for i, EbN0_db in enumerate(EbN0_db_range):

    bpsk_symbols = 2 * bits - 1

    ask_symbols = bits.astype(float)

    EbN0_linear = 10 ** (EbN0_db / 10)

    sigma_bpsk = np.sqrt(1 / (2 * EbN0_linear))
    sigma_ask = np.sqrt(0.5 / (2 * EbN0_linear))

    noise_bpsk = sigma_bpsk * np.random.randn(N)
    noise_ask = sigma_ask * np.random.randn(N)

    received_bpsk = bpsk_symbols + noise_bpsk
    received_ask = ask_symbols + noise_ask

    demod_bits_bpsk = (received_bpsk > 0).astype(int)
    demod_bits_ask = (received_ask > 0.5).astype(int)

    errors_bpsk = np.sum(bits != demod_bits_bpsk)
    errors_ask = np.sum(bits != demod_bits_ask)

    ber_bpsk_simulated[i] = errors_bpsk / N
    ber_ask_simulated[i] = errors_ask / N

    ber_bpsk_theoretical[i] = norm.sf(np.sqrt(2 * EbN0_linear))
    ber_ask_theoretical[i] = norm.sf(np.sqrt(EbN0_linear))

    if EbN0_db == 5:
        example_bits = bits[:100].copy()
        example_ask_symbols = ask_symbols[:100].copy()
        example_received_ask = received_ask[:100].copy()
        example_received_bpsk_constellation = received_bpsk.copy()
        example_received_ask_constellation = received_ask.copy()
        example_snr_value = EbN0_db

fig, axs = plt.subplots(2, 3, figsize=(18, 10))
fig.suptitle(f"BPSK и ASK (N={N} бит)", fontsize=16)


axs[0, 0].plot(
    example_ask_symbols,
    "bo-",
    label="Исходные символы ASK (0/1)",
    drawstyle="steps-post",
)
axs[0, 0].plot(
    example_received_ask,
    "r.-",
    alpha=0.7,
    label=f"Принятые символы ASK (Eb/N0={example_snr_value} дБ)",
)
axs[0, 0].set_title("Пример сигнала ASK")
axs[0, 0].set_xlabel("Индекс символа")
axs[0, 0].set_ylabel("Амплитуда")
axs[0, 0].legend()
axs[0, 0].grid(True)
axs[0, 0].set_ylim(-1.5, 2.5)


axs[0, 1].scatter(
    example_received_bpsk_constellation,
    np.zeros(N),
    alpha=0.3,
    label=f"Принятые символы (Eb/N0={example_snr_value} дБ)",
)
axs[0, 1].scatter(
    [-1, 1], [0, 0], c="red", marker="X", s=100, label="Идеальные символы (-1, +1)"
)
axs[0, 1].set_title("Созвездие BPSK")
axs[0, 1].set_xlabel("In-Phase (I)")
axs[0, 1].set_ylabel("Quadrature (Q)")
axs[0, 1].legend()
axs[0, 1].grid(True)
axs[0, 1].set_yticks([])
axs[0, 1].set_xlim(-3, 3)


axs[0, 2].scatter(
    example_received_ask_constellation,
    np.zeros(N),
    alpha=0.3,
    label=f"Принятые символы (Eb/N0={example_snr_value} дБ)",
)
axs[0, 2].scatter(
    [0, 1], [0, 0], c="red", marker="X", s=100, label="Идеальные символы (0, 1)"
)
axs[0, 2].set_title("Созвездие ASK")
axs[0, 2].set_xlabel("In-Phase (I)")
axs[0, 2].set_ylabel("Quadrature (Q)")
axs[0, 2].legend()
axs[0, 2].grid(True)
axs[0, 2].set_yticks([])
axs[0, 2].set_xlim(-1.5, 2.5)


axs[1, 0].semilogy(EbN0_db_range, ber_bpsk_simulated, "bo-", label="BPSK (симуляция)")
axs[1, 0].semilogy(EbN0_db_range, ber_bpsk_theoretical, "b--", label="BPSK (теория)")
axs[1, 0].semilogy(EbN0_db_range, ber_ask_simulated, "rs-", label="ASK (симуляция)")
axs[1, 0].semilogy(EbN0_db_range, ber_ask_theoretical, "r--", label="ASK (теория)")
axs[1, 0].set_title("BER vs Eb/N0")
axs[1, 0].set_xlabel("Eb/N0 (дБ)")
axs[1, 0].set_ylabel("Bit Error Rate (BER)")
axs[1, 0].legend()
axs[1, 0].grid(True, which="both")
axs[1, 0].set_ylim(1e-5, 1.0)


axs[1, 1].axis("off")
info_text = (
    f"Параметры симуляции:\n"
    f"Количество бит (N): {N}\n"
    f"Диапазон Eb/N0: {EbN0_db_range[0]} - {EbN0_db_range[-1]} дБ\n\n"
    f"Результаты BER при Eb/N0 = {EbN0_db_range[-1]} дБ:\n"
    f"BPSK (симул.): {ber_bpsk_simulated[-1]:.2e}\n"
    f"BPSK (теория): {ber_bpsk_theoretical[-1]:.2e}\n"
    f"ASK (симул.):  {ber_ask_simulated[-1]:.2e}\n"
    f"ASK (теория):  {ber_ask_theoretical[-1]:.2e}\n\n"
    f"Теоретические формулы:\n"
    f"BPSK: BER = Q(sqrt(2*Eb/N0))\n"
    f"ASK: BER = Q(sqrt(Eb/N0))"
)

axs[1, 1].text(
    0.05,
    0.95,
    info_text,
    transform=axs[1, 1].transAxes,
    fontsize=10,
    verticalalignment="top",
    bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.5),
)
axs[1, 1].set_title("Информация")


hist_snr_index = len(EbN0_db_range) // 2
hist_snr_db = EbN0_db_range[hist_snr_index]


EbN0_linear_hist = 10 ** (hist_snr_db / 10)
sigma_bpsk_hist = np.sqrt(1 / (2 * EbN0_linear_hist))
sigma_ask_hist = np.sqrt(0.5 / (2 * EbN0_linear_hist))
noise_bpsk_hist = sigma_bpsk_hist * np.random.randn(N)
noise_ask_hist = sigma_ask_hist * np.random.randn(N)
received_bpsk_hist = (2 * bits - 1) + noise_bpsk_hist
received_ask_hist = bits.astype(float) + noise_ask_hist

axs[1, 2].hist(
    received_bpsk_hist, bins=50, density=True, alpha=0.6, label="BPSK Принятые"
)
axs[1, 2].hist(
    received_ask_hist, bins=50, density=True, alpha=0.6, label="ASK Принятые"
)
axs[1, 2].set_title(f"Гистограммы принятых сигналов (Eb/N0={hist_snr_db} дБ)")
axs[1, 2].set_xlabel("Амплитуда")
axs[1, 2].set_ylabel("Плотность вероятности")
axs[1, 2].legend()
axs[1, 2].grid(True)


plt.tight_layout(rect=[0, 0.03, 1, 0.95])
plt.show()
