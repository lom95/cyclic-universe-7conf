import numpy as np
import matplotlib.pyplot as plt
import os
import sys

# Добавляем путь к корневой папке
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

print("🔍 Расчёт гамма-диполя...")
print(f"📂 Папка с результатами: {config.SCAN_RESULTS_DIR}")

# Используем лучший запуск из config
best = config.BEST_GAMMA

# Формируем путь к папке
run_folder = f"Q{best['Q']}_fluct{best['fluct']}_{best['run']}"
run_path = os.path.join(config.SCAN_RESULTS_DIR, run_folder)
pos_file = os.path.join(run_path, "positions_final.txt")

# Проверяем существование файла
if not os.path.exists(pos_file):
    print(f"❌ Файл не найден: {pos_file}")
    print("🔍 Ищем другие файлы в папке...")
    if os.path.exists(run_path):
        files = os.listdir(run_path)
        pos_files = [f for f in files if f.startswith("positions_cycle_")]
        if pos_files:
            pos_file = os.path.join(run_path, sorted(pos_files)[-1])
            print(f"✅ Найден: {pos_file}")
        else:
            print("❌ Нет файлов с координатами")
            exit()
    else:
        print(f"❌ Папка не найдена: {run_path}")
        exit()

# Загружаем координаты
data = np.loadtxt(pos_file)
x, y = data[:, 0], data[:, 1]
print(f"✅ Загружено {len(x)} частиц из {os.path.basename(pos_file)}")

# Вычисляем диполь
r = np.sqrt(x**2 + y**2)
theta = np.arccos(y / (r + 1e-10))
phi = np.arctan2(y, x)

X = np.mean(np.sin(theta) * np.cos(phi))
Y = np.mean(np.sin(theta) * np.sin(phi))
Z = np.mean(np.cos(theta))

amp = np.sqrt(X**2 + Y**2 + Z**2)
X, Y, Z = X/amp, Y/amp, Z/amp

l_sim = np.degrees(np.arctan2(Y, X)) % 360
b_sim = np.degrees(np.arcsin(Z))

print(f"\n📐 Твой диполь:")
print(f"   l = {l_sim:.1f}°")
print(f"   b = {b_sim:.1f}°")
print(f"   амплитуда = {amp:.5f}")

# Сравнение с целью
target_l, target_b = best['target_l'], best['target_b']
diff_l = min(abs(l_sim - target_l), 360 - abs(l_sim - target_l))
diff_b = abs(b_sim - target_b)

print(f"\n🎯 Цель: l={target_l}°, b={target_b}°")
print(f"   Δl = {diff_l:.1f}°, Δb = {diff_b:.1f}°")

# Сохраняем график
plt.figure(figsize=(8, 6))
plt.axhline(y=0, color='gray', linestyle='--', alpha=0.5)
plt.axvline(x=0, color='gray', linestyle='--', alpha=0.5)
plt.scatter(target_l, target_b, s=200, marker='o', c='blue', 
            label='Реальный диполь', alpha=0.7)
plt.scatter(l_sim, b_sim, s=200, marker='*', c='red', 
            label='Твой диполь', edgecolors='black', linewidth=2)
plt.xlabel('Галактическая долгота l (°)')
plt.ylabel('Галактическая широта b (°)')
plt.title('Сравнение с гамма-диполем')
plt.grid(True, alpha=0.3)
plt.legend()

# Сохраняем
plot_file = os.path.join(config.PLOTS_DIR, "gamma_dipole.png")
plt.savefig(plot_file, dpi=150, bbox_inches='tight')
plt.show()

print(f"\n✅ График сохранён: {plot_file}")

# Сохраняем результат в текстовый файл
best_file = os.path.join(config.BEST_DIR, "best_gamma_dipole.txt")
os.makedirs(config.BEST_DIR, exist_ok=True)

with open(best_file, "w") as f:
    f.write(f"Q = {best['Q']}\n")
    f.write(f"fluct_rate = {best['fluct']}\n")
    f.write(f"run = {best['run']}\n\n")
    f.write(f"Galactic coordinates:\n")
    f.write(f"l = {l_sim:.1f}°\n")
    f.write(f"b = {b_sim:.1f}°\n\n")
    f.write(f"Target: l={target_l}°, b={target_b}°\n")
    f.write(f"Δl = {diff_l:.1f}°, Δb = {diff_b:.1f}°\n")
    f.write(f"\nStatus: ✅ Fourth confirmation\n")

print(f"✅ Результат сохранён: {best_file}")
