import math
import argparse

def cost231_hata(fc_mhz, d_km, hb, hm, city="medium"):
    """
    COST-231 Hata model
    fc_mhz : частота, MHz (валидный диапазон 1500-2000)
    d_km   : расстояние, км (валидный диапазон 1-20)
    hb     : высота базовой станции, м (валидный диапазон 30-200)
    hm     : высота мобильной станции, м (валидный диапазон 1-10)
    city   : 'small', 'medium', 'large'

    Возвращает path loss в dB
    """
    if city == "large":
        C_m = 3
    else:
        C_m = 0

    if city == "large":
        if fc_mhz <= 200: 
            a_hm = 8.29 * (math.log10(1.54*hm))**2 - 1.1
        else:
            a_hm = 3.2 * (math.log10(11.75*hm))**2 - 4.97
    else: 
        a_hm = (1.1*math.log10(fc_mhz) - 0.7)*hm - (1.56*math.log10(fc_mhz) - 0.8)

    L = (46.3
         + 33.9*math.log10(fc_mhz)
         - 13.82*math.log10(hb)
         - a_hm
         + (44.9 - 6.55*math.log10(hb))*math.log10(d_km)
         + C_m) 

    return L

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="COST-231 Hata path loss calculator")
    parser.add_argument("--fc", type=float, default=2680, help="frequency in MHz (valid: 1500-2000)")
    parser.add_argument("--d", type=float, required=True, help="distance in km (valid: 1-20)")
    parser.add_argument("--hb", type=float, default=30.0, help="BS antenna height in m (valid: 30-200)")
    parser.add_argument("--hm", type=float, default=1.5, help="UE antenna height in m (valid: 1-10)")
    parser.add_argument("--city", choices=["small","medium","large"], default="medium")
    args = parser.parse_args()

    loss_db = cost231_hata(args.fc, args.d, args.hb, args.hm, args.city)
    print(f"Path loss = {loss_db:.2f} dB")