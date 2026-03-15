import numpy as np
import matplotlib.pyplot as plt
import os

# --- ПУТЬ К ЛУЧШЕМУ СПЕКТРУ ---
# Укажи здесь правильный путь к spectrum_final.txt из лучшего запуска
best_path = r"C:\Users\Fulgore\Desktop\cyclic_universe\results\scan_results_full\Q0.0102_fluct0.007_0\spectrum_final.txt"

# --- 1. ТВОЙ СПЕКТР ---
try:
    data_sim = np.loadtxt(best_path, comments='#')
    r_sim = data_sim[:, 0]
    density_sim = data_sim[:, 1]
    print(f"✅ Загружен твой спектр: {best_path}")
except:
    print(f"❌ Не могу найти {best_path}")
    exit()

# --- 2. ДАННЫЕ PLANCK ---
file_planck = "COM_PowerSpect_CMB-base-plikHM-TTTEEE-lowl-lowE-lensing-minimum-theory_R3.01.txt"
try:
    data_planck = np.loadtxt(file_planck, comments='#')
    l_planck = data_planck[:, 0]
    tt_planck = data_planck[:, 1]
    print(f"✅ Загружены данные Planck: {file_planck}")
except:
    print(f"❌ Не могу найти {file_planck}")
    exit()

# --- 3. МАСШТАБИРОВАНИЕ ---
scale = np.max(tt_planck) / np.max(density_sim)
r_scaled = r_sim * 100

# --- 4. ГРАФИК ---
plt.figure(figsize=(14, 7))
plt.plot(l_planck, tt_planck, 'b-', linewidth=1, label='Planck TT')
plt.plot(r_scaled, density_sim * scale, 'r-', linewidth=2, label='Твоя модель')
plt.xscale('log')
plt.xlabel('Мультиполь l')
plt.ylabel('$D_l$')
plt.title('Сравнение с Planck (лучший запуск Q=0.0103, fluct=0.005)')
plt.grid(True, alpha=0.3)
plt.legend()
plt.axvline(x=200, color='gray', linestyle='--', alpha=0.5)
plt.axvline(x=500, color='gray', linestyle='--', alpha=0.5)
plt.axvline(x=800, color='gray', linestyle='--', alpha=0.5)
plt.show()
