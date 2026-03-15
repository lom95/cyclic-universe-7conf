import numpy as np
import matplotlib.pyplot as plt
import glob
import os
import sys
from scipy.interpolate import interp1d

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

print("🔍 Поиск лучшего запуска по Planck...")
print(f"📂 Папка с результатами: {config.SCAN_RESULTS_DIR}")
print(f"📂 Данные Planck: {config.PLANCK_FILE}")

# === Загрузка Planck ===
data_planck = np.loadtxt(config.PLANCK_FILE, skiprows=50)
l_planck = data_planck[:, 0]
dl_planck = data_planck[:, 1]

# === Все папки ===
result_dirs = glob.glob(os.path.join(config.SCAN_RESULTS_DIR, "Q*_fluct*_*"))
print(f"📂 Найдено папок: {len(result_dirs)}")

results = []

for dirpath in result_dirs:
    folder = os.path.basename(dirpath)
    
    # Ищем спектр
    spec_files = glob.glob(os.path.join(dirpath, "spectrum_*.txt"))
    if not spec_files:
        continue
    
    spec_file = sorted(spec_files)[-1]
    data_sim = np.loadtxt(spec_file, comments='#')
    r_sim = data_sim[:, 0]
    power_sim = data_sim[:, 1]
    
    # Интерполяция Planck
    interp_func = interp1d(l_planck, dl_planck, kind='cubic',
                           bounds_error=False, fill_value='extrapolate')
    planck_interp = interp_func(r_sim)
    
    # Отклонение
    valid = np.isfinite(planck_interp) & np.isfinite(power_sim)
    if np.sum(valid) == 0:
        continue
    
    diff = np.sqrt(np.mean((power_sim[valid] - planck_interp[valid])**2))
    
    # Парсим параметры из имени
    try:
        parts = folder.split('_')
        Q = float(parts[0].replace('Q', ''))
        fluct = float(parts[1].replace('fluct', ''))
        run = int(parts[2])
    except:
        Q, fluct, run = 0, 0, 0
    
    results.append((diff, Q, fluct, run, folder))

# === Топ-5 ===
results.sort(key=lambda x: x[0])

print("\n🏆 ТОП-5 ПО PLANCK:")
print("="*60)
for i, (diff, Q, fluct, run, folder) in enumerate(results[:5]):
    print(f"\n{i+1}. {folder}")
    print(f"   Q = {Q:.4f}, fluct = {fluct:.3f}, run = {run}")
    print(f"   Отклонение: {diff:.4e}")

# === Сохраняем ===
best_file = os.path.join(config.BEST_DIR, "best_planck_found.txt")
with open(best_file, "w") as f:
    f.write("# rank\tdiff\tQ\tfluct\trun\tfolder\n")
    for i, (diff, Q, fluct, run, folder) in enumerate(results[:5]):
        f.write(f"{i+1}\t{diff:.4e}\t{Q:.4f}\t{fluct:.3f}\t{run}\t{folder}\n")

print(f"\n✅ Результаты сохранены в {best_file}")