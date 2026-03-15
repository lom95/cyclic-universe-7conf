import numpy as np
import matplotlib.pyplot as plt
import glob
from astropy.io.votable import parse
from scipy.stats import gaussian_kde

# === 1. ЗАГРУЗКА РЕАЛЬНЫХ СКОПЛЕНИЙ ===
print("📡 Загружаем MCXC-II...")
votable = parse("vizier_votable.vot")
table = votable.get_first_table().to_table()
ra_real = np.array(table['RAJ2000'])
dec_real = np.array(table['DEJ2000'])
print(f"✅ Реальных скоплений: {len(ra_real)}")

# === 2. ЗАГРУЗКА ТВОИХ ДАННЫХ ===
sim_files = glob.glob("positions_5000.txt")
if not sim_files:
    print("❌ Нет файлов positions_cycle_*.txt")
    exit()

latest = sorted(sim_files)[-1]
sim_data = np.loadtxt(latest)
sim_x, sim_y = sim_data[:, 0], sim_data[:, 1]
print(f"✅ Загружено {len(sim_x)} частиц из {latest}")

# === 3. ПОИСК ПЛОТНЫХ СГУСТКОВ ===
xy = np.vstack([sim_x, sim_y])
z = gaussian_kde(xy)(xy)
threshold = np.percentile(z, 20)  # топ-20% по плотности
dense = z > threshold
cluster_x = sim_x[dense]
cluster_y = sim_y[dense]
print(f"✅ Плотных сгустков: {len(cluster_x)}")

# === 4. НОРМАЛИЗАЦИЯ ===
def normalize(x, y):
    x_norm = (x - np.mean(x)) / np.std(x)
    y_norm = (y - np.mean(y)) / np.std(y)
    return x_norm, y_norm

ra_norm, dec_norm = normalize(ra_real, dec_real)
cx_norm, cy_norm = normalize(cluster_x, cluster_y)

# === 5. ВИЗУАЛИЗАЦИЯ ===
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# Твои сгустки
axes[0].scatter(cx_norm, cy_norm, s=2, alpha=0.5, c='red')
axes[0].set_title(f'Твои плотные сгустки ({len(cluster_x)})')
axes[0].set_xlabel('x (норм.)')
axes[0].set_ylabel('y (норм.)')
axes[0].set_aspect('equal')
axes[0].grid(alpha=0.3)

# Реальные скопления
axes[1].scatter(ra_norm, dec_norm, s=2, alpha=0.5, c='blue')
axes[1].set_title(f'Реальные скопления MCXC-II ({len(ra_real)})')
axes[1].set_xlabel('RA (норм.)')
axes[1].set_ylabel('Dec (норм.)')
axes[1].set_aspect('equal')
axes[1].grid(alpha=0.3)

plt.tight_layout()
plt.show()

# === 6. СТАТИСТИКА ===
print("\n📊 Сравнение:")
print(f"   Твоих частиц всего: {len(sim_x)}")
print(f"   Твоих сгустков: {len(cluster_x)} ({len(cluster_x)/len(sim_x)*100:.1f}% от всех)")
print(f"   Реальных скоплений: {len(ra_real)}")