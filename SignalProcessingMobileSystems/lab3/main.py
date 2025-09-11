import math
import pandas as pd

Pr_required_dBm = -73.426
Pt_given_dBm = 35.0
Gt_dB = 5.0
Gr_dB = 1.0
sigma_s_dB = 6.0
rho = 3.5
d0_m = 100.0

def Pl_d_dB(d_m, rho=rho, d0_m=d0_m):
    return 74.0 + 10.0 * rho * math.log10(d_m / d0_m)

def Phi(x):
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))

def outage_probability(Pt_dBm, d_m):
    Pl = Pl_d_dB(d_m)
    Pr_mean = Pt_dBm + Gt_dB + Gr_dB - Pl
    z = (Pr_required_dBm - Pr_mean) / sigma_s_dB
    return Phi(z), Pr_mean, Pl

for d_km in [1,2,5]:
    d_m = d_km * 1000.0
    Pout, Pr_mean, Pl = outage_probability(Pt_given_dBm, d_m)
    print(f"d={d_km} km: Pl={Pl:.3f} dB, Pr_mean={Pr_mean:.3f} dBm, P_out={Pout:.6f}")

p_target = 0.01
try:
    from math import erfinv
    z_star = math.sqrt(2.0) * erfinv(2.0 * p_target - 1.0)
except Exception:
    lo, hi = -10.0, 10.0
    for _ in range(100):
        mid = 0.5*(lo+hi)
        if Phi(mid) > p_target:
            hi = mid
        else:
            lo = mid
    z_star = 0.5*(lo+hi)

d_target_m = 3.0*1000.0
Pl_3km = Pl_d_dB(d_target_m)
Pt_min_needed = Pr_required_dBm - z_star * sigma_s_dB + Pl_3km - Gt_dB - Gr_dB
print("Pt_needed (d=3km, P_out<0.01) = {:.3f} dBm".format(Pt_min_needed))
