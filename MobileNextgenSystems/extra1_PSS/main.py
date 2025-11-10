import numpy as np
import matplotlib.pyplot as plt


def generate_pss(nid: int) -> np.ndarray:
    """
    Генерирует первичный сигнал синхронизации (PSS) для заданного NID.
    """
    u_map = {0: 25, 1: 29, 2: 34}
    if nid not in u_map:
        raise ValueError("NID должен быть 0, 1 или 2")
    u = u_map[nid]
    d = np.zeros(62, dtype=complex)
    for n in range(62):
        if n <= 30:
            d[n] = np.exp(-1j * np.pi * u * n * (n + 1) / 63)
        else:
            d[n] = np.exp(-1j * np.pi * u * (n + 1) * (n + 2) / 63)
    return d

def plot_constellations(pss_sequences: dict):
    """
    Строит и сохраняет констелляционные диаграммы для PSS.
    """
    fig, axes = plt.subplots(3, 3, figsize=(12, 12))
    fig.suptitle('Диаграммы PSS', fontsize=16, y=0.95)

    for nid, pss in pss_sequences.items():
        axes[nid, 0].plot(pss[:31].real, pss[:31].imag, 'ko', markerfacecolor='k')
        axes[nid, 0].set_title(f'NID={nid}, n=0..30')
        axes[nid, 1].plot(pss[31:].real, pss[31:].imag, 'bo', markerfacecolor='b')
        axes[nid, 1].set_title(f'NID={nid}, n=31..61')
        axes[nid, 2].plot(pss.real, pss.imag, 'ro', markerfacecolor='r')
        axes[nid, 2].set_title(f'NID={nid}, n=0..61')

    for ax in axes.flat:
        ax.set_aspect('equal', adjustable='box')
        ax.set_xlim(-1.5, 1.5)
        ax.set_ylim(-1.5, 1.5)
        ax.grid(True)

def plot_cross_correlation(pss_sequences: dict):
    """
    Строит и сохраняет графики кросс-корреляции между PSS(NID=0) и другими PSS.
    """
    fig, axes = plt.subplots(3, 1, figsize=(10, 8), sharex=True)
    fig.suptitle('Кросс-корреляция между PSS', fontsize=16)
    pss_nid0 = pss_sequences[0]
    titles = [
        'Автокорреляция: PSS(NID=0) с PSS(NID=0)',
        'Кросс-корреляция: PSS(NID=0) с PSS(NID=1)',
        'Кросс-корреляция: PSS(NID=0) с PSS(NID=2)'
    ]

    for i in range(3):
        corr_full = np.correlate(pss_nid0, pss_sequences[i], mode='full')
        corr_positive_lags = corr_full[len(pss_nid0)-1:]
        corr_magnitude = np.abs(corr_positive_lags)

        axes[i].stem(corr_magnitude)
        axes[i].set_title(titles[i])
        axes[i].set_ylabel('Амплитуда')
        axes[i].set_ylim(0, 70)
        axes[i].grid(True)

    axes[-1].set_xlabel('Сдвиг (lags)')
    plt.tight_layout(rect=[0, 0, 1, 0.96])

def plot_correlation_matrix(pss_sequences: dict):
    """
    Вычисляет и строит матрицу пиковых корреляций между всеми PSS.
    """
    nids = list(pss_sequences.keys())
    num_seqs = len(nids)
    corr_matrix = np.zeros((num_seqs, num_seqs))
    for i in range(num_seqs):
        for j in range(num_seqs):
            seq1 = pss_sequences[nids[i]]
            seq2 = pss_sequences[nids[j]]
            correlation_result = np.correlate(seq1, seq2, mode='full')
            peak_value = np.max(np.abs(correlation_result))
            corr_matrix[i, j] = peak_value

    fig, ax = plt.subplots(figsize=(8, 6))
    im = ax.imshow(corr_matrix, cmap='viridis')
    cbar = fig.colorbar(im)
    cbar.set_label('Пиковое значение корреляции', rotation=270, labelpad=15)
    ax.set_xticks(np.arange(num_seqs))
    ax.set_yticks(np.arange(num_seqs))
    ax.set_xticklabels([f'PSS (NID={n})' for n in nids])
    ax.set_yticklabels([f'PSS (NID={n})' for n in nids])
    ax.set_title('Матрица пиковых корреляций PSS')
    for i in range(num_seqs):
        for j in range(num_seqs):
            ax.text(j, i, f'{corr_matrix[i, j]:.1f}',
                    ha='center', va='center', color='white')

    fig.tight_layout()

if __name__ == "__main__":
    all_pss = {nid: generate_pss(nid) for nid in range(3)}
    try:
        with open("pss_roots.txt", "w", encoding="utf-8") as f:
            f.write("Комплексные значения PSS для каждого NID\n")
            f.write("========================================\n\n")
            for nid, pss_seq in all_pss.items():
                f.write(f"----- NID = {nid} -----\n")
                for i, val in enumerate(pss_seq):
                    f.write(f"d({i:02d}): {val.real:+.4f} {val.imag:+.4f}j\n")
                f.write("\n")
        print("Результаты сохранены в файл 'pss_roots.txt'.")
    except IOError as e:
        print(f"Ошибка при записи в файл: {e}")

    plot_constellations(all_pss)
    plot_cross_correlation(all_pss)
    plot_correlation_matrix(all_pss)

    plt.show()