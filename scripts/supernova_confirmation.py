"""
Подтверждение 6: Сверхновые Ia
Модель с отрицательной массой и фиксированным w = -1
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import quad
from scipy.optimize import curve_fit
import os
import warnings
warnings.filterwarnings("ignore")

# ==================== ЗАГРУЗКА ДАННЫХ ====================

def load_data():
    """Загружает данные из локального файла supernova_data.txt"""
    
    filename = "supernova_data.txt"
    
    if not os.path.exists(filename):
        print(f"❌ Файл {filename} не найден!")
        print("📥 Создай файл supernova_data.txt и скопируй туда данные:")
        print("   z    mu    error")
        print("   0.01 33.73 0.20")
        print("   0.012 34.10 0.19")
        print("   ... (41 строка)")
        return None, None, None
    
    try:
        data = np.loadtxt(filename, skiprows=1)
        z = data[:, 0]
        mu = data[:, 1]
        error = data[:, 2]
        print(f"✅ Загружено {len(z)} сверхновых")
        print(f"   z от {np.min(z):.3f} до {np.max(z):.3f}")
        return z, mu, error
    except Exception as e:
        print(f"❌ Ошибка чтения: {e}")
        return None, None, None

# ==================== МОДЕЛЬ С ФИКСИРОВАННЫМ w = -1 ====================

def H_z(z, H0, Omega_m):
    """
    Параметр Хаббла H(z) с w = -1 (как у тебя из подгонки a(t))
    Плоская Вселенная: Omega_q = 1 - Omega_m
    """
    Omega_q = 1 - Omega_m
    return H0 * np.sqrt(Omega_m * (1+z)**3 + Omega_q)

def distance_modulus(z, H0, Omega_m):
    """
    Модуль расстояния μ(z) = 5 log₁₀(d_L / 10 pc)
    """
    def integrand(zp):
        return 1 / H_z(zp, H0, Omega_m)
    
    try:
        integral, _ = quad(integrand, 0, z)
        c = 299792.458  # скорость света в км/с
        d_L = (1+z) * integral * c  # в Мпк
        return 5 * np.log10(d_L * 1e5)
    except:
        return np.nan

# ==================== ПОДГОНКА ====================

def fit_model(z_data, mu_data, mu_error):
    """
    Подбирает только H0 и Omega_m (w = -1 фиксировано)
    """
    p0 = [70, 0.3]  # начальное приближение: H0, Omega_m
    
    def model(z, H0, Omega_m):
        return np.array([distance_modulus(z[i], H0, Omega_m) for i in range(len(z))])
    
    try:
        popt, pcov = curve_fit(model, z_data, mu_data, p0=p0, sigma=mu_error, maxfev=5000)
        H0_fit, Omega_m_fit = popt
        perr = np.sqrt(np.diag(pcov))
        
        print(f"\n📊 ПОДОБРАНО (w = -1 фиксировано):")
        print(f"   H₀ = {H0_fit:.2f} ± {perr[0]:.2f} км/с/Мпк")
        print(f"   Ω_m = {Omega_m_fit:.3f} ± {perr[1]:.3f}")
        
        return popt, perr
    except Exception as e:
        print(f"❌ Ошибка подгонки: {e}")
        return None, None

# ==================== ВИЗУАЛИЗАЦИЯ ====================

def plot_results(z, mu, error, popt):
    """
    Строит график сравнения
    """
    H0_fit, Omega_m_fit = popt
    
    plt.figure(figsize=(14, 10))
    
    # 1. Главный график
    plt.subplot(2, 2, 1)
    plt.errorbar(z, mu, yerr=error, fmt='.', color='black', alpha=0.5, 
                 label=f'Данные ({len(z)} сверхновых)', markersize=4)
    
    z_model = np.linspace(0, max(z), 100)
    mu_model = np.array([distance_modulus(zi, H0_fit, Omega_m_fit) for zi in z_model])
    plt.plot(z_model, mu_model, 'r-', linewidth=2, label='Модель (w = -1)')
    
    plt.xlabel('Красное смещение z', fontsize=12)
    plt.ylabel('Модуль расстояния μ', fontsize=12)
    plt.title('Сверхновые Ia: данные vs модель с отрицательной массой', fontsize=14)
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # 2. Остатки
    plt.subplot(2, 2, 2)
    mu_pred = np.array([distance_modulus(zi, H0_fit, Omega_m_fit) for zi in z])
    residuals = mu - mu_pred
    plt.errorbar(z, residuals, yerr=error, fmt='.', color='blue', alpha=0.5, markersize=4)
    plt.axhline(y=0, color='red', linestyle='--', linewidth=2)
    plt.xlabel('Красное смещение z', fontsize=12)
    plt.ylabel('Остатки Δμ', fontsize=12)
    plt.title('Отклонение модели от данных', fontsize=14)
    plt.grid(True, alpha=0.3)
    
    # 3. Гистограмма остатков
    plt.subplot(2, 2, 3)
    plt.hist(residuals, bins=15, color='green', alpha=0.7, edgecolor='black')
    plt.axvline(x=0, color='red', linestyle='--')
    plt.xlabel('Δμ', fontsize=12)
    plt.ylabel('Количество', fontsize=12)
    plt.title('Распределение остатков', fontsize=14)
    plt.grid(True, alpha=0.3)
    
    # 4. Информация о подгонке
    plt.subplot(2, 2, 4)
    plt.axis('off')
    
    chi2 = np.sum((residuals / error)**2)
    dof = len(z) - len(popt)
    chi2dof = chi2 / dof
    
    info = f"РЕЗУЛЬТАТЫ ПОДГОНКИ\n\n"
    info += f"H₀ = {H0_fit:.2f} км/с/Мпк\n"
    info += f"Ω_m = {Omega_m_fit:.3f}\n"
    info += f"(w = -1 фиксировано)\n\n"
    info += f"χ² = {chi2:.2f}\n"
    info += f"DoF = {dof}\n"
    info += f"χ²/DoF = {chi2dof:.2f}\n\n"
    
    if chi2dof < 1.5:
        info += "✅ Отличное согласие!"
    elif chi2dof < 2.5:
        info += "✅ Хорошее согласие"
    elif chi2dof < 3.5:
        info += "⚠️ Приемлемо"
    else:
        info += "❌ Плохое согласие"
    
    plt.text(0.1, 0.9, info, transform=plt.gca().transAxes,
             fontsize=12, verticalalignment='top',
             bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    plt.tight_layout()
    plt.savefig('supernova_confirmation.png', dpi=150)
    plt.show()
    
    return chi2, dof, chi2dof

# ==================== ОСНОВНАЯ ПРОГРАММА ====================

def main():
    print("="*70)
    print("🔭 ПОДТВЕРЖДЕНИЕ 6: СВЕРХНОВЫЕ Ia (w = -1 фиксировано)")
    print("="*70)
    
    # Загружаем данные
    z, mu, error = load_data()
    if z is None:
        return
    
    # Подгоняем модель
    popt, perr = fit_model(z, mu, error)
    if popt is None:
        return
    
    # Строим графики и получаем статистику
    chi2, dof, chi2dof = plot_results(z, mu, error, popt)
    
    # Сохраняем результат
    with open('supernova_result.txt', 'w') as f:
        f.write("РЕЗУЛЬТАТЫ ПОДТВЕРЖДЕНИЯ 6: СВЕРХНОВЫЕ Ia\n")
        f.write("="*60 + "\n\n")
        f.write(f"Модель: плоская Вселенная с отрицательной массой (w = -1)\n\n")
        f.write(f"Подогнанные параметры:\n")
        f.write(f"   H₀ = {popt[0]:.2f} ± {perr[0]:.2f} км/с/Мпк\n")
        f.write(f"   Ω_m = {popt[1]:.3f} ± {perr[1]:.3f}\n\n")
        f.write(f"Статистика:\n")
        f.write(f"   χ² = {chi2:.2f}\n")
        f.write(f"   DoF = {dof}\n")
        f.write(f"   χ²/DoF = {chi2dof:.2f}\n\n")
        
        if chi2dof < 2:
            f.write("✅ МОДЕЛЬ ПОДТВЕРЖДАЕТСЯ данными сверхновых!\n")
            f.write("   6-е подтверждение получено.\n")
        elif chi2dof < 3:
            f.write("⚠️ Согласие приемлемое. Модель не противоречит данным.\n")
        else:
            f.write("❌ Модель плохо согласуется с данными.\n")
    
    print("\n" + "="*70)
    print("✅ АНАЛИЗ ЗАВЕРШЁН")
    print("📊 График: supernova_confirmation.png")
    print("📝 Результат: supernova_result.txt")
    print("="*70)

if __name__ == "__main__":
    main()
