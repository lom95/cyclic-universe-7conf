"""
Анализ барионных акустических осцилляций (BAO)
с автоматическим подбором масштаба
"""

import numpy as np
import matplotlib.pyplot as plt
import os
from scipy.spatial.distance import pdist
from scipy.ndimage import gaussian_filter1d
import warnings
warnings.filterwarnings("ignore")

# ==================== НАСТРОЙКИ ====================
NBINS = 50               # число бинов гистограммы
SMOOTH_SIGMA = 2         # сглаживание
BAO_REAL = 700.0         # реальный пик BAO в Мпк
# ===================================================

def load_positions(filename):
    """Загружает координаты частиц из файла"""
    
    if not os.path.exists(filename):
        print(f"❌ Файл {filename} не найден!")
        return None
    
    data = np.loadtxt(filename, skiprows=1)
    print(f"✅ Загружено {len(data)} частиц из {filename}")
    return data

def compute_correlation(positions):
    """
    Вычисляет двухточечную корреляционную функцию ξ(r)
    """
    print("   Считаю попарные расстояния...")
    
    # Берём только x,y
    coords = positions[:, :2]
    
    # Все попарные расстояния
    distances = pdist(coords)
    
    print(f"   Получено {len(distances)} пар")
    
    # Определяем масштаб симуляции
    sim_size = np.max(coords) - np.min(coords)
    print(f"📏 Размер симуляции: {sim_size:.2e}")
    
    # Масштабный фактор для перевода в Мпк
    scale_factor = BAO_REAL / sim_size
    print(f"📏 SCALE_FACTOR = {scale_factor:.6e}")
    
    # Переводим расстояния в Мпк
    distances_mpc = distances * scale_factor
    
    # Гистограмма
    hist, edges = np.histogram(distances_mpc, bins=NBINS)
    r_center = (edges[:-1] + edges[1:]) / 2
    dr = edges[1] - edges[0]
    
    # Нормировка на случайное распределение (2D)
    area = sim_size**2 * scale_factor**2  # площадь в Мпк²
    expected = len(coords) * (len(coords) - 1) / 2 * (2 * np.pi * r_center * dr) / area
    
    # Корреляционная функция
    correlation = hist / expected - 1
    
    # Сглаживание
    correlation = gaussian_filter1d(correlation, sigma=SMOOTH_SIGMA)
    
    return r_center, correlation, scale_factor

def find_bao_peak(r, corr):
    """
    Находит пик BAO в корреляционной функции
    """
    # Ищем локальный максимум после 20% диапазона
    start_idx = len(r) // 5
    peak_idx = start_idx + np.argmax(corr[start_idx:])
    
    return r[peak_idx], corr[peak_idx]

def plot_bao(r, corr, peak_r, peak_val, scale_factor):
    """
    Строит график корреляционной функции
    """
    plt.figure(figsize=(14, 7))
    
    # Основной график
    plt.subplot(1, 2, 1)
    plt.plot(r, corr, 'b-', linewidth=2, label='Симуляция')
    plt.axhline(y=0, color='k', linestyle='--', alpha=0.5)
    
    # Отмечаем пик
    plt.plot(peak_r, peak_val, 'ro', markersize=10, label=f'Пик: {peak_r:.1f} Мпк')
    
    # Реальные данные SDSS
    plt.axvline(x=105, color='gray', linestyle=':', alpha=0.7, label='SDSS пики')
    plt.axvline(x=150, color='gray', linestyle=':', alpha=0.7)
    
    plt.xlabel('Расстояние (Мпк)', fontsize=12)
    plt.ylabel('Корреляционная функция ξ(r)', fontsize=12)
    plt.title('BAO в симуляции', fontsize=14)
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.xlim(0, min(300, np.max(r)))
    
    # График зависимости от масштаба
    plt.subplot(1, 2, 2)
    plt.plot(r * scale_factor, corr, 'g-', linewidth=2)
    plt.axhline(y=0, color='k', linestyle='--', alpha=0.5)
    plt.axvline(x=peak_r * scale_factor, color='r', linestyle='--', alpha=0.5)
    plt.xlabel('Расстояние (единицы симуляции)', fontsize=12)
    plt.ylabel('ξ(r)', fontsize=12)
    plt.title('Исходный масштаб симуляции', fontsize=14)
    plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('bao_analysis_fixed.png', dpi=150)
    plt.show()
    
    print(f"📊 График сохранён в bao_analysis_fixed.png")

def compare_with_sdss(peak_r):
    """
    Сравнивает найденный пик с данными SDSS
    """
    sdss_peaks = [105, 150]  # основные пики BAO
    tolerance = 20  # допуск в Мпк
    
    print("\n📊 СРАВНЕНИЕ С SDSS:")
    print(f"   Пик в симуляции: {peak_r:.1f} Мпк")
    print(f"   SDSS пики: {sdss_peaks[0]} Мпк, {sdss_peaks[1]} Мпк")
    
    for sdss in sdss_peaks:
        if abs(peak_r - sdss) < tolerance:
            print(f"✅ СОВПАДЕНИЕ с пиком {sdss} Мпк!")
            return True
    
    print("⚠️ Пик не совпадает с SDSS в пределах допуска.")
    return False

# ==================== ОСНОВНАЯ ПРОГРАММА ====================

def main():
    print("="*60)
    print("🔭 АНАЛИЗ BAO (автоматический масштаб)")
    print("="*60)
    
    # Ищем самый свежий файл с координатами
    files = [f for f in os.listdir() if f.startswith("positions_cycle_")]
    if not files:
        print("❌ Нет файлов positions_cycle_*.txt")
        return
    
    latest = sorted(files)[-1]
    print(f"📁 Использую файл: {latest}")
    
    # Загружаем
    positions = load_positions(latest)
    if positions is None:
        return
    
    # Считаем корреляцию
    r, corr, scale_factor = compute_correlation(positions)
    
    # Ищем пик
    peak_r, peak_val = find_bao_peak(r, corr)
    print(f"\n📌 Найден пик BAO на расстоянии: {peak_r:.1f} Мпк")
    
    # Рисуем
    plot_bao(r, corr, peak_r, peak_val, scale_factor)
    
    # Сравниваем с SDSS
    match = compare_with_sdss(peak_r)
    
    # Сохраняем результат
    with open("bao_result.txt", "w") as f:
        f.write("РЕЗУЛЬТАТЫ АНАЛИЗА BAO\n")
        f.write("="*50 + "\n\n")
        f.write(f"Файл данных: {latest}\n")
        f.write(f"Частиц: {len(positions)}\n")
        f.write(f"Масштабный фактор: {scale_factor:.6e}\n")
        f.write(f"Пик BAO: {peak_r:.2f} Мпк\n")
        f.write(f"Совпадение с SDSS: {'ДА' if match else 'НЕТ'}\n")
    
    print("\n✅ Анализ завершён!")
    print("📝 Результаты сохранены в bao_result.txt")

if __name__ == "__main__":
    main()