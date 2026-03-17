"""
Подтверждение 7: Постоянная Хаббла H₀
"""

import numpy as np
import matplotlib.pyplot as plt

def main():
    print("="*60)
    print("ПОДТВЕРЖДЕНИЕ 7: ПОСТОЯННАЯ ХАББЛА H0")
    print("="*60)
    
    # Значение из модели (из подгонки сверхновых)
    h0_model = 79.93
    h0_error = 2.74
    
    # Сравнительные измерения
    measurements = {
        'Planck (CMB)': (67.4, 0.5),
        'SH0ES (сверхновые)': (73.0, 1.0),
        'H0LiCOW (линзы)': (73.3, 1.8),
        'Эта работа': (h0_model, h0_error)
    }
    
    # Построение графика
    plt.figure(figsize=(10, 6))
    x_pos = 0
    colors = ['blue', 'red', 'green', 'black']
    
    for (name, (val, err)), color in zip(measurements.items(), colors):
        plt.errorbar(x_pos, val, yerr=err, fmt='o', color=color, 
                    capsize=5, markersize=10, label=f'{name}: {val:.1f}±{err:.1f}')
        x_pos += 1
    
    # Опорные линии
    plt.axhline(y=67.4, color='gray', linestyle='--', alpha=0.5, label='Planck (67.4)')
    plt.axhline(y=73.0, color='gray', linestyle='--', alpha=0.5, label='SH0ES (73.0)')
    
    plt.xlim(-0.5, len(measurements) - 0.5)
    plt.xticks(range(len(measurements)), measurements.keys(), rotation=15)
    plt.ylabel('H₀ (км/с/Мпк)')
    plt.title('Сравнение постоянной Хаббла')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig("plots/h0_comparison.png", dpi=150)
    plt.show()
    
    # Расчет совместимости
    print("\nСОВМЕСТИМОСТЬ С ИЗМЕРЕНИЯМИ:")
    print("-" * 40)
    
    for name, (val, err) in measurements.items():
        if name == 'Эта работа':
            continue
        diff = abs(h0_model - val)
        sigma = diff / np.sqrt(h0_error**2 + err**2)
        print(f"{name}: разница {diff:.2f} км/с/Мпк ({sigma:.2f} сигма)")
    
    # Интерпретация
    print("\nИНТЕРПРЕТАЦИЯ:")
    sh0es_sigma = abs(h0_model - 73.0) / np.sqrt(h0_error**2 + 1.0**2)
    if sh0es_sigma < 2:
        print(f"✓ Модель согласуется с поздними измерениями (SH0ES: {sh0es_sigma:.2f} сигма)")
        print("  7-е подтверждение ПОЛУЧЕНО!")
    else:
        print(f"Модель ближе к Planck (разница {abs(h0_model-67.4):.2f})")
    
    # Сохранение результатов
    with open("h0_result.txt", "w") as f:
        f.write("РЕЗУЛЬТАТЫ ПОДТВЕРЖДЕНИЯ 7: ПОСТОЯННАЯ ХАББЛА H₀\n")
        f.write("="*50 + "\n\n")
        f.write(f"H₀ из модели = {h0_model:.2f} ± {h0_error:.2f} км/с/Мпк\n\n")
        
        for name, (val, err) in measurements.items():
            if name == 'Эта работа':
                f.write(f"\n{name}: {val:.2f} ± {err:.2f}\n")
            else:
                diff = abs(h0_model - val)
                sigma = diff / np.sqrt(h0_error**2 + err**2)
                f.write(f"{name}: {val:.1f} ± {err:.1f} (разница: {diff:.2f}, {sigma:.2f} сигма)\n")
    
    print("\nПОДТВЕРЖДЕНИЕ 7 ЗАВЕРШЕНО")
    print("График сохранен в plots/h0_comparison.png")
    print("Результаты сохранены в h0_result.txt")

if __name__ == "__main__":
    main()