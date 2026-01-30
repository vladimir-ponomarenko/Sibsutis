import os
import numpy as np
import scipy.io as sp
import numpy.linalg as la

# ==========================================
# 1. Загрузка данных
# ==========================================
filename = "H16_4_35.mat"
script_dir = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(script_dir, filename)

if not os.path.exists(file_path):
    print(f"Файл {filename} не найден.")
else:
    Hmatr = sp.loadmat(file_path)
    vals = list(Hmatr.values())
    h_full = next((v for v in vals if isinstance(v, np.ndarray) and v.ndim == 3), None)
    if h_full is None:
        print("Ошибка структуры файла.")

print(f"Размерность данных канала: {h_full.shape}")

subcarrier_idx = 0
user_indices = [0, 1, 2, 3]

h1 = h_full[:, subcarrier_idx, user_indices[0]]
h2 = h_full[:, subcarrier_idx, user_indices[1]]
h3 = h_full[:, subcarrier_idx, user_indices[2]]
h4 = h_full[:, subcarrier_idx, user_indices[3]]

h1 = h1 / la.norm(h1)
h2 = h2 / la.norm(h2)
h3 = h3 / la.norm(h3)
h4 = h4 / la.norm(h4)

# ==========================================
# 2. Вычисление векторов прекодирования
# ==========================================

H = np.zeros((16, 4), dtype='complex')
H[:, 0] = h1
H[:, 1] = h2
H[:, 2] = h3
H[:, 3] = h4

# 1. Транспонируем (Users x Antennas) -> (4 x 16)
H_users = H.T

# 2. Вычисляем псевдообратную матрицу
# W = H^H * (H * H^H)^-1
H1 = H_users.conj().T          # H^H (Эрмитово сопряжение) (16 x 4)
H2 = H_users @ H1              # H * H^H (Матрица Грама) (4 x 4)
W_unnorm = H1 @ la.inv(H2)     # Результирующая матрица весов (16 x 4)

w1 = W_unnorm[:, 0]
w1 = w1 / la.norm(w1)

w2 = W_unnorm[:, 1]
w2 = w2 / la.norm(w2)

w3 = W_unnorm[:, 2]
w3 = w3 / la.norm(w3)

w4 = W_unnorm[:, 3]
w4 = w4 / la.norm(w4)

W0 = np.zeros((16, 4), dtype='complex')
W0[:, 0] = w1
W0[:, 1] = w2
W0[:, 2] = w3
W0[:, 3] = w4

# ==========================================
# 3. Проверка условия ортогональности
# ==========================================
print("\n--- Пункт 3: Проверка ортогональности (каналы vs прекодеры) ---")
# H_users (4x16) @ W0 (16x4) -> Ik (4x4)
Ik = H_users @ W0

print("Результирующая матрица H * W:")
print(np.round(np.abs(Ik), 2))

off_diagonal_elements = Ik[~np.eye(Ik.shape[0], dtype=bool)]
avg_interference = np.mean(np.abs(off_diagonal_elements))

if avg_interference < 1e-6:
    print(">> Условие ортогональности выполнено (Интерференция подавлена).")
else:
    print(">> Интерференция присутствует.")

# ==========================================
# 4. Проверка подавления интерференции
# ==========================================
print("\n--- Пункт 4: Проверка подавления интерференции ---")

# Проверка 1: Чужой канал (Интерференция)
interference_val = np.dot(h2.T, w1)
print(f"Интерференция (Канал 2 принимает Сигнал 1): {np.abs(interference_val):.6f}")

# Проверка 2: Свой канал (Полезный сигнал)
signal_val = np.dot(h1.T, w1)
print(f"Полезный сигнал (Канал 1 принимает Сигнал 1): {np.abs(signal_val):.6f}")

# Проверка 3: Еще одна пара (Канал 3 и Сигнал 4)
interf_34 = np.dot(h3.T, w4)
print(f"Интерференция (Канал 3 принимает Сигнал 4): {np.abs(interf_34):.6f}")