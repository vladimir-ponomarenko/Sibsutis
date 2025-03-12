import os
import numpy as np
import scipy.io as sp
import matplotlib.pyplot as plt


script_dir = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(script_dir, "H16_1.mat")

if not os.path.exists(file_path):
    print("Файл не найден.")
    # H_full = np.random.randn(8, 8, 512, 10) + 1j * np.random.randn(8, 8, 512, 10)
else:
    Hmatr = sp.loadmat(file_path)
    H_full = Hmatr['H16']

Nr = 4
Nt = 4
subcarrier_idx = 0
snapshot_idx = 0
H_raw = H_full[:Nr, :Nt, subcarrier_idx, snapshot_idx]
norm_val = np.linalg.norm(H_raw, 'fro')
H = H_raw / norm_val

print("Матрица канала H (после нормализации):\n", H)

U, S, Vh = np.linalg.svd(H)
r = np.sum(S > 1e-6)
print(f"\nРанг (r): {r}")
print(f"Сингулярные числа: {S}")

SNR_dB = np.arange(0, 25)
SNR_lin = 10**(SNR_dB / 10.0)

C_SISO = []
C_MIMO = []
C_BF = []

h_siso = H[0, 0]
for snr in SNR_lin:
    c_siso = np.log2(1 + snr * (np.abs(h_siso)**2))
    C_SISO.append(c_siso)

    c_mimo = np.sum(np.log2(1 + (S[:r]**2) * snr / r))
    C_MIMO.append(c_mimo)

    sigma_max = np.max(S)
    c_bf = np.log2(1 + (sigma_max**2) * snr  / r)
    C_BF.append(c_bf)

plt.figure(figsize=(10, 6))
plt.plot(SNR_dB, C_MIMO, label='MIMO 4x4 (Multiplexing)', linewidth=2.5, marker='o', markersize=4)
plt.plot(SNR_dB, C_BF, label='Beamforming (Max singular val)', linewidth=2, linestyle='--', marker='s', markersize=4)
plt.plot(SNR_dB, C_SISO, label='SISO', linewidth=2, linestyle='-.', marker='x', markersize=4)

plt.title('Зависимость пропускной способности от SNR')
plt.xlabel('SNR (Ex/N0), дБ')
plt.ylabel('Пропускная способность')
plt.legend()
plt.grid(True, which="both", ls="-")
plt.show()