import numpy as np
import matplotlib.pyplot as plt


C = 3 * 10**8  # Скорость света, м/с
THERMAL_NOISE_FLOOR_DBM_HZ = -174  # Уровень теплового шума, дБм/Гц

class NetworkPlanner:
    def __init__(self, power_bs_transmitter_dbm=46, sectors_per_bs=3,
                 power_ue_transmitter_dbm=24, antenna_gain_bs_dbi=21,
                 penetration_loss_db=15, interference_margin_db=1,
                 frequency_ghz=1.8, bandwidth_ul_mhz=10,
                 bandwidth_dl_mhz=20, noise_figure_bs_db=2.4,
                 noise_figure_ue_db=6, sinr_dl_db=2, sinr_ul_db=4,
                 mimo_antennas_bs=2, area_total_km2=100,
                 area_business_centers_km2=4, feeder_loss_db=2):
        
        # Параметры сети
        self.power_bs_transmitter_dbm = power_bs_transmitter_dbm
        self.sectors_per_bs = sectors_per_bs
        self.power_ue_transmitter_dbm = power_ue_transmitter_dbm
        self.antenna_gain_bs_dbi = antenna_gain_bs_dbi
        self.penetration_loss_db = penetration_loss_db
        self.interference_margin_db = interference_margin_db
        self.frequency_ghz = frequency_ghz
        self.bandwidth_ul_mhz = bandwidth_ul_mhz
        self.bandwidth_dl_mhz = bandwidth_dl_mhz
        self.noise_figure_bs_db = noise_figure_bs_db
        self.noise_figure_ue_db = noise_figure_ue_db
        self.sinr_dl_db = sinr_dl_db
        self.sinr_ul_db = sinr_ul_db
        self.mimo_antennas_bs = mimo_antennas_bs
        self.area_total_km2 = area_total_km2
        self.area_business_centers_km2 = area_business_centers_km2
        self.feeder_loss_db = feeder_loss_db

        # Вычисляемые параметры
        self.frequency_hz = self.frequency_ghz * 10**9
        self.bandwidth_ul_hz = self.bandwidth_ul_mhz * 10**6
        self.bandwidth_dl_hz = self.bandwidth_dl_mhz * 10**6
        self.thermal_noise_dl = self._calculate_thermal_noise(self.bandwidth_dl_hz)
        self.thermal_noise_ul = self._calculate_thermal_noise(self.bandwidth_ul_hz)
        self.sensitivity_bs_dbm = self._calculate_sensitivity(self.thermal_noise_dl, self.sinr_dl_db, self.noise_figure_bs_db)
        self.sensitivity_ue_dbm = self._calculate_sensitivity(self.thermal_noise_ul, self.sinr_ul_db, self.noise_figure_ue_db)
        self.mimo_gain_db = self._calculate_mimo_gain(self.mimo_antennas_bs)
        self.max_path_loss_dl = self._calculate_max_path_loss(self.power_bs_transmitter_dbm, self.feeder_loss_db,
                                                               self.antenna_gain_bs_dbi, self.mimo_gain_db,
                                                               self.penetration_loss_db, self.interference_margin_db,
                                                               self.sensitivity_ue_dbm)
        self.max_path_loss_ul = self._calculate_max_path_loss(self.power_ue_transmitter_dbm, self.feeder_loss_db,
                                                               self.antenna_gain_bs_dbi, self.mimo_gain_db,
                                                               self.penetration_loss_db, self.interference_margin_db,
                                                               self.sensitivity_bs_dbm)

        print(f"Уровень максимально допустимых потерь сигнала MAPL_UL: {self.max_path_loss_ul:.2f} дБ")
        print(f"Уровень максимально допустимых потерь сигнала MAPL_DL: {self.max_path_loss_dl:.2f} дБ")

    def _calculate_thermal_noise(self, bandwidth_hz):
        return THERMAL_NOISE_FLOOR_DBM_HZ + 10 * np.log10(bandwidth_hz)

    def _calculate_sensitivity(self, thermal_noise, sinr_db, noise_figure_db):
        return thermal_noise + sinr_db + noise_figure_db

    def _calculate_mimo_gain(self, mimo_antennas):
        return 10 * np.log10(mimo_antennas)

    def _calculate_max_path_loss(self, tx_power_dbm, feeder_loss_db, antenna_gain_dbi,
                                  mimo_gain_db, penetration_loss_db, interference_margin_db,
                                  sensitivity_dbm):
        return tx_power_dbm - feeder_loss_db + antenna_gain_dbi + mimo_gain_db - \
               penetration_loss_db - interference_margin_db - sensitivity_dbm

    def _plot_path_loss(self, distances, path_loss, model_name, *args):
        plt.plot(distances, path_loss, *args, label=model_name)

    def plot_umi_nlos(self):
        distances = np.arange(1, 5000)
        path_loss_umi = 26 * np.log10(self.frequency_ghz) + 22.7 + 36.7 * np.log10(distances)
        path_loss_fspl = self._calculate_fspl(distances)
        
        plt.figure(1)
        self._plot_path_loss(distances, path_loss_umi, "UMiNLOS")
        self._plot_path_loss(distances, path_loss_fspl, "FSPM", "--")
        plt.axhline(y=self.max_path_loss_dl, color='r', linestyle='-', label="MAPL_DL")
        plt.axhline(y=self.max_path_loss_ul, color='y', linestyle='--', label="MAPL_UL")

        self._configure_plot("Потери сигнала, дБ", "Расстояние между приемником и передатчиком, м")
        plt.show()

    def plot_cost_231(self):
        distances_m = np.arange(1, 10000)
        path_loss_cost = [self._calculate_cost_231(distance, "DU") for distance in distances_m]
        path_loss_fspl = self._calculate_fspl(distances_m)

        plt.figure(2)
        self._plot_path_loss(distances_m, path_loss_cost, "COST 231")
        self._plot_path_loss(distances_m, path_loss_fspl, "FSPM", "--")
        plt.axhline(y=self.max_path_loss_dl, color='r', linestyle='-', label="MAPL_DL")
        plt.axhline(y=self.max_path_loss_ul, color='y', linestyle='--', label="MAPL_UL")

        self._configure_plot("Потери сигнала, дБ", "Расстояние между приемником и передатчиком, м")
        plt.show()

    def plot_all_models(self):
        distances_m = np.arange(1, 10000)
        distances_km = distances_m / 1000

        path_loss_umi = 26 * np.log10(self.frequency_ghz) + 22.7 + 36.7 * np.log10(distances_m)
        path_loss_walfish = 42.6 + 20 * np.log10(self.frequency_ghz * 10**3) + 26 * np.log10(distances_km)
        path_loss_cost = [self._calculate_cost_231(distance, "DU") for distance in distances_m]

        plt.figure(3)
        self._plot_path_loss(distances_m, path_loss_cost, "COST 231")
        self._plot_path_loss(distances_m, path_loss_umi, "UMiNLOS")
        self._plot_path_loss(distances_m, path_loss_walfish, "Walfish-Ikegami")
        plt.axhline(y=self.max_path_loss_dl, color='r', linestyle='--', label="MAPL_DL")
        plt.axhline(y=self.max_path_loss_ul, color='y', linestyle='--', label="MAPL_UL")

        self._configure_plot("Потери сигнала, дБ", "Расстояние между приемником и передатчиком, м")
        plt.show()

    def _calculate_fspl(self, distances):
        return 20 * np.log10((4 * np.pi * self.frequency_hz * distances) / C)

    def _clutter_loss(self, environment_type):
        if environment_type == "DU":
            return 3
        elif environment_type == "U":
            return 0
        elif environment_type == "SU":
            return -(2 * (np.log10(self.frequency_ghz * 10**3 / 28))**2 + 5.4)
        elif environment_type == "RURAL":
            return -(4.78 * (np.log10(self.frequency_ghz * 10**3))**2 - 18.33 * np.log10(self.frequency_ghz * 10**3) + 40.94)
        elif environment_type == "ROAD":
            return -(4.78 * (np.log10(self.frequency_ghz * 10**3))**2 - 18.33 * np.log10(self.frequency_ghz * 10**3) + 35.94)

    def _parameter_a(self, environment_type):
        mobile_height_m = 7.5
        if environment_type in ("DU", "U"):
            return 3.2 * (np.log10(11.75 * mobile_height_m))**2 - 4.97
        elif environment_type in ("SU", "RURAL", "ROAD"):
            return (1.1 * np.log10(self.frequency_ghz * 10**3) * mobile_height_m -
                    1.56 * np.log10(self.frequency_ghz * 10**3) - 0.8)

    def _parameter_s(self, distance_km, base_station_height_m=50):
        if distance_km >= 1:
            return 44.9 - 6.55 * np.log10(self.frequency_ghz * 10**3)
        else:
            return (47.88 + 13.9 * np.log10(self.frequency_ghz * 10**3) -
                    13.9 * np.log10(base_station_height_m)) * (1 / np.log10(50))

    def _calculate_cost_231(self, distance_m, environment_type):
        distance_km = distance_m * 10**-3
        return (46.3 + 33.9 * np.log10(self.frequency_ghz * 10**3) - 13.82 * np.log10(50) -
                self._parameter_a(environment_type) +
                self._parameter_s(distance_km, 50) * np.log10(distance_km) +
                self._clutter_loss(environment_type))

    def _configure_plot(self, ylabel, xlabel):
        plt.ylabel(ylabel)
        plt.xlabel(xlabel)
        plt.yticks(np.arange(0, 201, 50))
        plt.legend(loc=4)
        plt.grid(linewidth=0.5)

    def calculate_bs_coverage(self):
        radius_umi = 500 * 10**-3
        radius_cost = 900 * 10**-3

        area_umi = 1.95 * radius_umi**2
        area_cost = 1.95 * radius_cost**2

        print(f"Радиус Базовой станции для модели UMiNLOS = {radius_umi:.3f} км")
        print(f"Радиус Базовой станции для модели Cost231 = {radius_cost:.3f} км")
        print(f"Площадь одной базовой станции для модели UMiNLOS = {area_umi:.3f} км кв")
        print(f"Площадь одной базовой станции для модели Cost231 = {area_cost:.3f} км кв")

        bs_count_umi = self.area_business_centers_km2 / area_umi
        bs_count_cost = self.area_total_km2 / area_cost
        print(f"Необходимое количество базовых станций для модели UMiNLOS: {bs_count_umi:.2f}")
        print(f"Необходимое количество базовых станций для модели Cost231: {bs_count_cost:.2f}")

planner = NetworkPlanner()
planner.plot_umi_nlos()
planner.plot_cost_231()
planner.plot_all_models()
planner.calculate_bs_coverage()
