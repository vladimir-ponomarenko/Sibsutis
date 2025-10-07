import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

c = 3e8
fc = 2e9
lambda_wave = c / fc
N = 20
F = 16
dx = lambda_wave / F
v = 10

freq_band_mhz = [1997.5, 2002.5]
df_mhz = 0.01
freq_axis_hz = np.arange(freq_band_mhz[0], freq_band_mhz[1], df_mhz) * 1e6
Nf = len(freq_axis_hz)
bs_pos = np.array([1000, 1000])
sc1_pos = np.array([200, 500])
sc2_pos = np.array([-200, 500])
t = np.arange(N) * dx / v
ms_x = v * t
ms_pos = np.array([ms_x, np.zeros(N)])

def simulate_channel(sc1_pos, sc2_pos, a1, a2, scenario_name):
    d_bs_sc1 = np.linalg.norm(bs_pos - sc1_pos)
    d_bs_sc2 = np.linalg.norm(bs_pos - sc2_pos)
    d_sc1_ms = np.linalg.norm(sc1_pos[:, np.newaxis] - ms_pos, axis=0)
    d_sc2_ms = np.linalg.norm(sc2_pos[:, np.newaxis] - ms_pos, axis=0)
    tau1 = (d_bs_sc1 + d_sc1_ms) / c
    tau2 = (d_bs_sc2 + d_sc2_ms) / c

    H = a1 * np.exp(-1j * 2 * np.pi * freq_axis_hz[:, np.newaxis] * tau1) + \
        a2 * np.exp(-1j * 2 * np.pi * freq_axis_hz[:, np.newaxis] * tau2)

    impulse_response_t = np.fft.ifft(H, axis=0)
    impulse_response_t = np.fft.fftshift(impulse_response_t, axes=0)
    time_delay_axis_us = np.fft.fftshift(np.fft.fftfreq(Nf, d=df_mhz*1e6)) * 1e6

    return H, impulse_response_t, time_delay_axis_us, tau1, tau2

def plot_3d_channel_response(H, t, freq_axis_hz, scenario_name):
    """Построение 3D графика частотной характеристики"""
    fig = plt.figure(figsize=(12, 8))
    ax = fig.add_subplot(111, projection='3d')
    T, F = np.meshgrid(t, freq_axis_hz / 1e6)
    Z = np.abs(H)

    surf = ax.plot_surface(T, F, Z, cmap='viridis', alpha=0.8,
                          linewidth=0, antialiased=True)

    ax.set_xlabel('Время, с')
    ax.set_ylabel('Частота, МГц')
    ax.set_zlabel('|H(f,t)|')
    ax.set_title(f'3D график ЧХ: {scenario_name}')
    fig.colorbar(surf, ax=ax, shrink=0.5, aspect=5)
    plt.tight_layout()
    plt.show()

def plot_results(H, impulse_response_t, time_delay_axis_us, t, scenario_name, tau1, tau2):
    fig, axs = plt.subplots(4, 2, figsize=(16, 20), constrained_layout=True)
    fig.suptitle(f'Моделирование широкополосного двухлучевого канала\n{scenario_name}', fontsize=16)
    time_snapshot_idx = N // 2
    selected_time_s = t[time_snapshot_idx]
    freq_snapshot_idx = Nf // 2
    selected_freq_mhz = freq_axis_hz[freq_snapshot_idx] / 1e6

    ax = axs[0, 0]
    ax.plot(bs_pos[0], bs_pos[1], 'ro', markersize=10, label='BS')
    ax.plot(sc1_pos[0], sc1_pos[1], 'bs', markersize=8, label='SC1')
    ax.plot(sc2_pos[0], sc2_pos[1], 'gs', markersize=8, label='SC2')
    ax.plot(ms_pos[0, :], ms_pos[1, :], 'k-', linewidth=2, label='Траектория MS')
    ax.plot(ms_pos[0, time_snapshot_idx], ms_pos[1, time_snapshot_idx], 'ko',
            markersize=6, label=f'MS (t={selected_time_s:.2f} с)')
    ax.set_title('1. Диаграмма размещения')
    ax.set_xlabel('x, м'); ax.set_ylabel('y, м'); ax.legend(); ax.grid(True); ax.axis('equal')

    ax = axs[0, 1]
    im = ax.imshow(np.abs(H), aspect='auto', origin='lower',
                   extent=[t.min(), t.max(), freq_band_mhz[0], freq_band_mhz[1]],
                   cmap='hot')
    fig.colorbar(im, ax=ax, label='|H(f,t)|')
    ax.set_title('2. |ЧХ| по траектории (от времени и частоты)')
    ax.set_xlabel('Время, с'); ax.set_ylabel('Частота, МГц')

    ax = axs[1, 0]
    ax.plot(t, np.abs(H[freq_snapshot_idx, :]), 'b-', linewidth=2)
    ax.set_title(f'3. |ЧХ| от времени (на {selected_freq_mhz:.2f} МГц)')
    ax.set_xlabel('Время, с'); ax.set_ylabel('|H(t)|'); ax.grid(True)

    ax = axs[1, 1]
    ax.plot(freq_axis_hz / 1e6, np.abs(H[:, time_snapshot_idx]), 'r-', linewidth=2)
    ax.set_title(f'4. |ЧХ| по всей полосе (в t={selected_time_s:.2f} с)')
    ax.set_xlabel('Частота, МГц'); ax.set_ylabel('|H(f)|'); ax.grid(True)

    ax = axs[2, 0]
    ax.plot(freq_axis_hz / 1e6, np.angle(H[:, time_snapshot_idx]), 'g-', linewidth=2)
    ax.set_title(f'5. Фаза ЧХ по всей полосе (в t={selected_time_s:.2f} с)')
    ax.set_xlabel('Частота, МГц'); ax.set_ylabel('Фаза, рад'); ax.grid(True)

    ax = axs[2, 1]
    im = ax.imshow(np.abs(impulse_response_t), aspect='auto', origin='lower',
                   extent=[t.min(), t.max(), time_delay_axis_us.min(), time_delay_axis_us.max()],
                   cmap='viridis')
    fig.colorbar(im, ax=ax, label='|h(τ,t)|')
    ax.set_title('6. |ИХ| по траектории (от времени и задержки)')
    ax.set_xlabel('Время, с'); ax.set_ylabel('Задержка, мкс')

    ax = axs[3, 0]
    ax.plot(time_delay_axis_us, np.abs(impulse_response_t[:, time_snapshot_idx]), 'm-', linewidth=2)
    ax.set_title(f'7. |ИХ| в выбранной точке (t={selected_time_s:.2f} с)')
    ax.set_xlabel('Задержка, мкс'); ax.set_ylabel('|h(τ)|'); ax.grid(True)

    ax = axs[3, 1]
    ax.text(0.1, 0.8, f'Разность задержек лучей:\nΔτ = {abs(tau1[0]-tau2[0])*1e6:.2f} мкс',
            fontsize=12, transform=ax.transAxes)
    ax.text(0.1, 0.6, f'Задержки:\nτ1 = {tau1[0]*1e6:.2f} мкс\nτ2 = {tau2[0]*1e6:.2f} мкс',
            fontsize=10, transform=ax.transAxes)
    ax.text(0.1, 0.3, f'Коэффициенты:\nα1 = {a1}, α2 = {a2}',
            fontsize=12, transform=ax.transAxes)
    ax.text(0.1, 0.1, f'Параметры:\nN = {N} точек\nv = {v} м/с',
            fontsize=12, transform=ax.transAxes)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_title('8. Параметры моделирования')
    ax.axis('off')

    plt.show()

    return abs(tau1[0] - tau2[0]) * 1e6


print("=== СЦЕНАРИЙ 1: Исходные параметры ===")
a1, a2 = 1.0, 0.5
H1, impulse_response_t1, time_delay_axis_us1, tau1_1, tau2_1 = simulate_channel(
    sc1_pos, sc2_pos, a1, a2, "Исходные параметры")
delta_tau1 = plot_results(H1, impulse_response_t1, time_delay_axis_us1, t,
                         "Исходные параметры (α1=1.0, α2=0.5)", tau1_1, tau2_1)
plot_3d_channel_response(H1, t, freq_axis_hz, "Исходные параметры")

print("\n=== СЦЕНАРИЙ 2: Увеличенная разность задержек ===")
sc1_pos_new = np.array([200, 500])
sc2_pos_new = np.array([-800, 1500])
H2, impulse_response_t2, time_delay_axis_us2, tau1_2, tau2_2 = simulate_channel(
    sc1_pos_new, sc2_pos_new, a1, a2, "Увеличенная разность задержек")
delta_tau2 = plot_results(H2, impulse_response_t2, time_delay_axis_us2, t,
                         "Увеличенная разность задержек (α1=1.0, α2=0.5)", tau1_2, tau2_2)
plot_3d_channel_response(H2, t, freq_axis_hz, "Увеличенная разность задержек")

print("\n=== СЦЕНАРИЙ 3: Равные коэффициенты передачи ===")
a1_new, a2_new = 0.5, 0.5
H3, impulse_response_t3, time_delay_axis_us3, tau1_3, tau2_3 = simulate_channel(
    sc1_pos, sc2_pos, a1_new, a2_new, "Равные коэффициенты передачи")
delta_tau3 = plot_results(H3, impulse_response_t3, time_delay_axis_us3, t,
                         "Равные коэффициенты (α1=0.5, α2=0.5)", tau1_3, tau2_3)
plot_3d_channel_response(H3, t, freq_axis_hz, "Равные коэффициенты")

print(f"\nСравнение разностей задержек:")
print(f"Сценарий 1 (исходный): Δτ = {delta_tau1:.2f} мкс")
print(f"Сценарий 2 (увеличенная): Δτ = {delta_tau2:.2f} мкс")
print(f"Сценарий 3 (равные коэф.): Δτ = {delta_tau3:.2f} мкс")

print(f"\nАнализ задержек:")
print(f"Сценарий 1: τ1 = {tau1_1[0]*1e6:.2f} мкс, τ2 = {tau2_1[0]*1e6:.2f} мкс")
print(f"Сценарий 2: τ1 = {tau1_2[0]*1e6:.2f} мкс, τ2 = {tau2_2[0]*1e6:.2f} мкс")
print(f"Сценарий 3: τ1 = {tau1_3[0]*1e6:.2f} мкс, τ2 = {tau2_3[0]*1e6:.2f} мкс")

print("\n=== МОДЕЛИРОВАНИЕ С БОЛЬШИМ КОЛИЧЕСТВОМ РАССЕИВАТЕЛЕЙ ===")
num_scatterers = 50
scatterers_pos = np.random.uniform(-800, 800, (2, num_scatterers))
scatterers_amp = np.random.rayleigh(0.5, num_scatterers)

H_multi = np.zeros((Nf, N), dtype=complex)
for i in range(num_scatterers):
    d_bs_sc = np.linalg.norm(bs_pos - scatterers_pos[:, i])
    d_sc_ms = np.linalg.norm(scatterers_pos[:, i, np.newaxis] - ms_pos, axis=0)
    tau = (d_bs_sc + d_sc_ms) / c
    H_multi += scatterers_amp[i] * np.exp(-1j * 2 * np.pi * freq_axis_hz[:, np.newaxis] * tau)

impulse_response_multi = np.fft.ifft(H_multi, axis=0)
impulse_response_multi = np.fft.fftshift(impulse_response_multi, axes=0)

fig, axs = plt.subplots(2, 2, figsize=(15, 10), constrained_layout=True)
fig.suptitle('Моделирование с большим количеством рассеивателей (N=50)', fontsize=16)

ax = axs[0, 0]
ax.plot(bs_pos[0], bs_pos[1], 'ro', markersize=10, label='BS')
ax.plot(scatterers_pos[0, :], scatterers_pos[1, :], 'b.', markersize=4, label='Рассеиватели')
ax.plot(ms_pos[0, :], ms_pos[1, :], 'k-', linewidth=2, label='Траектория MS')
ax.set_title('Диаграмма размещения')
ax.set_xlabel('x, м'); ax.set_ylabel('y, м'); ax.legend(); ax.grid(True)

ax = axs[0, 1]
im = ax.imshow(np.abs(H_multi), aspect='auto', origin='lower',
               extent=[t.min(), t.max(), freq_band_mhz[0], freq_band_mhz[1]],
               cmap='hot')
fig.colorbar(im, ax=ax, label='|H(f,t)|')
ax.set_title('|ЧХ| по траектории')
ax.set_xlabel('Время, с'); ax.set_ylabel('Частота, МГц')

ax = axs[1, 0]
im = ax.imshow(np.abs(impulse_response_multi), aspect='auto', origin='lower',
               extent=[t.min(), t.max(), time_delay_axis_us1.min(), time_delay_axis_us1.max()],
               cmap='viridis')
fig.colorbar(im, ax=ax, label='|h(τ,t)|')
ax.set_title('|ИХ| по траектории')
ax.set_xlabel('Время, с'); ax.set_ylabel('Задержка, мкс')

ax = axs[1, 1]
mid_point = N // 2
ax.plot(time_delay_axis_us1, np.abs(impulse_response_multi[:, mid_point]), 'm-', linewidth=2)
ax.set_title(f'|ИХ| в средней точке (t={t[mid_point]:.2f} с)')
ax.set_xlabel('Задержка, мкс'); ax.set_ylabel('|h(τ)|'); ax.grid(True)

plt.show()

plot_3d_channel_response(H_multi, t, freq_axis_hz, "Множество рассеивателей (N=50)")