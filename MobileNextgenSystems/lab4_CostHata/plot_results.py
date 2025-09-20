#!/usr/bin/env python3
import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("results.csv")

x_labels = [f"{d} km ({pl:.1f} dB)" for d, pl in zip(df["distance_km"], df["pathloss_db"])]

fig, axes = plt.subplots(3, 1, figsize=(10, 10), sharex=True)

axes[0].plot(x_labels, df["rsrp_dbm"], marker="o", color="blue")
axes[0].set_title("RSRP vs Distance (COST-231 Hata)")
axes[0].set_ylabel("RSRP [dBm]")
axes[0].grid(True)

axes[1].plot(x_labels, df["rsrq_db"], marker="s", color="green")
axes[1].set_title("RSRQ vs Distance (COST-231 Hata)")
axes[1].set_ylabel("RSRQ [dB]")
axes[1].grid(True)

axes[2].plot(x_labels, df["sinr_db"], marker="^", color="red")
axes[2].set_title("SINR vs Distance (COST-231 Hata)")
axes[2].set_ylabel("SINR [dB]")
axes[2].set_xlabel("Distance (km) with Path Loss")
axes[2].grid(True)

plt.tight_layout()
plt.show()
