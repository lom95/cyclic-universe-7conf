import numpy as np
import glob
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

print("🔍 Поиск лучших запусков по гамма-диполю...")
print(f"📂 Папка с результатами: {config.SCAN_RESULTS_DIR}")
print("🎯 Цель: l ≈ 150°, b ≈ -5°\n")

# === Сбор всех папок ===
result_dirs = glob.glob(os.path.join(config.SCAN_RESULTS_DIR, "Q*_fluct*_*"))
print(f"📂 Найдено папок: {len(result_dirs)}")

if len(result_dirs) == 0:
    print("❌ Папки не найдены.")
    exit()

results = []
target_l, target_b = 150, -5

for dirpath in result_dirs:
    try:
        folder = os.path.basename(dirpath)
        parts = folder.split('_')
        Q = float(parts[0].replace('Q', ''))
        fluct = float(parts[1].replace('fluct', ''))
        run = int(parts[2])
    except Exception as e:
        continue

    pos_files = glob.glob(os.path.join(dirpath, "positions_final.txt"))
    if not pos_files:
        continue
    
    latest = sorted(pos_files)[-1]
    data = np.loadtxt(latest)
    x, y = data[:, 0], data[:, 1]

    r = np.sqrt(x**2 + y**2)
    theta = np.arccos(y / (r + 1e-10))
    phi = np.arctan2(y, x)

    X = np.mean(np.sin(theta) * np.cos(phi))
    Y = np.mean(np.sin(theta) * np.sin(phi))
    Z = np.mean(np.cos(theta))

    amp = np.sqrt(X**2 + Y**2 + Z**2)
    if amp > 0:
        X, Y, Z = X/amp, Y/amp, Z/amp

    l_sim = np.degrees(np.arctan2(Y, X)) % 360
    b_sim = np.degrees(np.arcsin(Z))

    diff_l = min(abs(l_sim - target_l), 360 - abs(l_sim - target_l))
    diff_b = abs(b_sim - target_b)
    total_error = diff_l + diff_b

    results.append((total_error, diff_l, diff_b, l_sim, b_sim, Q, fluct, run, folder))

# === Топ-10 ===
results.sort(key=lambda x: x[0])

print("\n🏆 ТОП-10 ЛУЧШИХ ЗАПУСКОВ (по близости к гамма-диполю)")
print("="*70)

if len(results) == 0:
    print("❌ Нет результатов с координатами.")
    exit()

best_gamma_file = os.path.join(config.BEST_DIR, "gamma_dipole_top10.txt")
with open(best_gamma_file, "w") as f:
    f.write("# rank\ttotal_error\tdl\tdb\tl\tb\tQ\tfluct\trun\tfolder\n")
    
    for i, (err, dl, db, l, b, Q, fluct, run, folder) in enumerate(results[:10]):
        status = "✅" if dl < 30 and db < 30 else "❌"
        print(f"\n{i+1}. {folder}")
        print(f"   l = {l:.1f}° (Δ={dl:.1f}°), b = {b:.1f}° (Δ={db:.1f}°)")
        print(f"   Суммарная ошибка: {err:.1f}° {status}")
        f.write(f"{i+1}\t{err:.1f}\t{dl:.1f}\t{db:.1f}\t{l:.1f}\t{b:.1f}\t{Q:.4f}\t{fluct:.3f}\t{run}\t{folder}\n")

print(f"\n✅ Топ-10 сохранён в {best_gamma_file}")

# === Сохраняем лучший ===
best = results[0]
best_info = {
    'Q': best[5],
    'fluct': best[6],
    'run': best[7],
    'l': best[3],
    'b': best[4],
    'dl': best[1],
    'db': best[2]
}

best_file = os.path.join(config.BEST_DIR, "best_gamma_dipole.txt")
with open(best_file, "w", encoding="utf-8") as f:
    f.write(f"Q = {best_info['Q']}\n")
    f.write(f"fluct_rate = {best_info['fluct']}\n")
    f.write(f"run = {best_info['run']}\n\n")
    f.write(f"Galactic coordinates:\n")
    f.write(f"l = {best_info['l']:.1f}° (delta_l = {best_info['dl']:.1f}°)\n")
    f.write(f"b = {best_info['b']:.1f}° (delta_b = {best_info['db']:.1f}°)\n\n")
    f.write(f"Target: l={target_l}°, b={target_b}°\n")
    status = "✅ Fourth confirmation" if best_info['dl'] < 30 and best_info['db'] < 30 else "❌ Not confirmed"
    f.write(f"\nStatus: {status}\n")

print(f"\n✅ Лучший запуск сохранён в {best_file}")
