import numpy as np
import matplotlib.pyplot as plt
from astroquery.sdss import SDSS
import os

# === 1. ЗАГРУЗКА ТВОИХ ДАННЫХ ИЗ СИМУЛЯЦИИ ===
sim_files = []
for f in os.listdir('.'):
    if f.startswith('positions_final') and f.endswith('.txt'):
        sim_files.append(f)

if not sim_files:
    print("❌ Нет файлов positions_cycle_.txt в папке!")
    exit()

print(f"✅ Найдено файлов симуляции: {len(sim_files)}")
# Берём последний (самый свежий)
latest_file = sorted(sim_files)[-1]
sim_data = np.loadtxt(latest_file)
sim_x, sim_y = sim_data[:, 0], sim_data[:, 1]
print(f"✅ Загружен {latest_file}, частиц: {len(sim_x)}")

# === 2. ЗАГРУЗКА ДАННЫХ SDSS ===
print("📡 Загружаем данные SDSS...")
query = """
SELECT TOP 10000
  ra, dec
FROM SpecObj
WHERE class = 'GALAXY' AND z BETWEEN 0.01 AND 0.5
"""
try:
    data = SDSS.query_sql(query)
    if data is None:
        print("❌ Не удалось загрузить SDSS")
        exit()
    ra_sdss = np.array(data['ra'])
    dec_sdss = np.array(data['dec'])
    print(f"✅ Загружено {len(ra_sdss)} галактик из SDSS")
except Exception as e:
    print(f"❌ Ошибка загрузки SDSS: {e}")
    exit()

# === 3. ПОДГОТОВКА К СРАВНЕНИЮ ===
# Нормализуем координаты твоей симуляции
sim_x_norm = (sim_x - np.mean(sim_x)) / np.std(sim_x)
sim_y_norm = (sim_y - np.mean(sim_y)) / np.std(sim_y)

# Нормализуем координаты SDSS
ra_norm = (ra_sdss - np.mean(ra_sdss)) / np.std(ra_sdss)
dec_norm = (dec_sdss - np.mean(dec_sdss)) / np.std(dec_sdss)

# === 4. ВИЗУАЛИЗАЦИЯ ===
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# Твоя симуляция
axes[0].scatter(sim_x_norm, sim_y_norm, s=1, alpha=0.5, c='red')
axes[0].set_title(f'Твоя модель ({latest_file})')
axes[0].set_xlabel('x (норм.)')
axes[0].set_ylabel('y (норм.)')
axes[0].grid(alpha=0.3)
axes[0].set_aspect('equal')

# Данные SDSS
axes[1].scatter(ra_norm, dec_norm, s=1, alpha=0.3, c='blue')
axes[1].set_title('SDSS галактики (10000)')
axes[1].set_xlabel('RA (норм.)')
axes[1].set_ylabel('Dec (норм.)')
axes[1].grid(alpha=0.3)
axes[1].set_aspect('equal')

plt.tight_layout()
plt.show()

# === 5. СТАТИСТИКА ===
print("\n📊 Сравнение распределений:")
print(f"   Твоя модель: {len(sim_x)} точек")
print(f"   SDSS: {len(ra_sdss)} галактик")
print(f"   Разброс (твоя): x={np.std(sim_x):.3f}, y={np.std(sim_y):.3f}")
print(f"   Разброс (SDSS): RA={np.std(ra_sdss):.3f}, Dec={np.std(dec_sdss):.3f}")
