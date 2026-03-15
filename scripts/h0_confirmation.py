"""
Подтверждение 7: Постоянная Хаббла H₀
Сравнение значения из модели с реальными измерениями
"""

import numpy as np
import matplotlib.pyplot as plt

# ==================== ДАННЫЕ ====================

# Измерения H₀
h0_data = {
    'Планк (CMB)': {'value': 67.4, 'error': 0.5, 'color': 'blue'},
    'SH0ES (сверхновые)': {'value': 73.0, 'error': 1.0, 'color': 'red'},
    'H0LiCOW (линзы)': {'value': 73.3, 'error': 1.8, 'color': 'green'},
    'TRGB (звёзды)': {'value': 69.8, 'error': 1.9, 'color': 'purple'},
}

# Твоя модель (из подгонки сверхновых)
h0_model = 79.93
h0_model_error = 2.74

# ==================== ВИЗУАЛИЗАЦИЯ ====================

def plot_h0_comparison():
    """Строит график сравнения H₀"""
    
    plt.figure(figsize=(12, 6))
    
    # Реальные измерения
    x_pos = 0
    for name, data in h0_data.items():
        plt.errorbar(x_pos, data['value'], yerr=data['error'], 
                    fmt='o', color=data['color'], capsize=5, 
                    markersize=10, label=name)
        x_pos += 1
    
    # Твоя модель
    plt.errorbar(x_pos, h0_model, yerr=h0_model_error,
                fmt='s', color='black', capsize=5,
                markersize=12, label='ТВОЯ МОДЕЛЬ')
    
    plt.axhline(y=67.4, color='gray', linestyle='--', alpha=0.5, label='Планк (67.4)')
    plt.axhline(y=73.0, color='gray', linestyle='--', alpha=0.5, label='SH0ES (73.0)')
    
    plt.xlim(-0.5, len(h0_data) + 0.5)
    plt.xticks(range(len(h0_data) + 1), 
               list(h0_data.keys()) + ['Твоя модель'], 
               rotation=45, ha='right')
    plt.ylabel('H₀ (км/с/Мпк)', fontsize=14)
    plt.title('Сравнение постоянной Хаббла: данные vs твоя модель', fontsize=16)
    plt.legend(loc='upper right')
    plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('h0_confirmation.png', dpi=150)
    plt.show()

def calculate_compatibility():
    """Вычисляет совместимость с разными измерениями"""
    
    print("\n📊 СОВМЕСТИМОСТЬ С ИЗМЕРЕНИЯМИ:")
    print("-" * 50)
    
    for name, data in h0_data.items():
        diff = abs(h0_model - data['value'])
        sigma = diff / np.sqrt(h0_model_error**2 + data['error']**2)
        
        print(f"{name}:")
        print(f"   Разница: {diff:.2f} км/с/Мпк")
        print(f"   Сигма: {sigma:.2f}σ")
        
        if sigma < 1:
            print("   ✅ Отличное согласие")
        elif sigma < 2:
            print("   ✅ Хорошее согласие")
        elif sigma < 3:
            print("   ⚠️ Приемлемое")
        else:
            print("   ❌ Расхождение")
        print()
    
    # Сравнение с Planck и SH0ES (главные)
    planck_sigma = abs(h0_model - 67.4) / np.sqrt(h0_model_error**2 + 0.5**2)
    sh0es_sigma = abs(h0_model - 73.0) / np.sqrt(h0_model_error**2 + 1.0**2)
    
    print("ГЛАВНЫЙ РЕЗУЛЬТАТ:")
    if sh0es_sigma < 2:
        print(f"✅ Модель совпадает с поздними измерениями (SH0ES: {sh0es_sigma:.2f}σ)")
        print(f"   7-е подтверждение ПОЛУЧЕНО!")
    else:
        print(f"⚠️ Модель ближе к Planck ({planck_sigma:.2f}σ), чем к SH0ES")

# ==================== ОСНОВНАЯ ПРОГРАММА ====================

def main():
    print("="*60)
    print("🔭 ПОДТВЕРЖДЕНИЕ 7: ПОСТОЯННАЯ ХАББЛА H₀")
    print("="*60)
    
    print(f"\n📌 Значение из твоей модели: H₀ = {h0_model:.2f} ± {h0_model_error:.2f}")
    
    # Строим график
    plot_h0_comparison()
    
    # Считаем совместимость
    calculate_compatibility()
    
    # Сохраняем результат
    with open('h0_result.txt', 'w') as f:
        f.write("РЕЗУЛЬТАТЫ ПОДТВЕРЖДЕНИЯ 7: H₀\n")
        f.write("="*50 + "\n\n")
        f.write(f"Модель: H₀ = {h0_model:.2f} ± {h0_model_error:.2f} км/с/Мпк\n\n")
        
        for name, data in h0_data.items():
            diff = abs(h0_model - data['value'])
            sigma = diff / np.sqrt(h0_model_error**2 + data['error']**2)
            f.write(f"{name}: {data['value']} ± {data['error']}\n")
            f.write(f"   Разница: {diff:.2f} ({sigma:.2f}σ)\n")
        
        sh0es_sigma = abs(h0_model - 73.0) / np.sqrt(h0_model_error**2 + 1.0**2)
        if sh0es_sigma < 2:
            f.write("\n✅ МОДЕЛЬ ПОДТВЕРЖДАЕТСЯ (совпадает с SH0ES)\n")
            f.write("   7-е подтверждение получено.\n")
        else:
            f.write("\n⚠️ Совместимость умеренная.\n")
    
    print("\n" + "="*60)
    print("✅ АНАЛИЗ ЗАВЕРШЁН")
    print("📊 График: h0_confirmation.png")
    print("📝 Результат: h0_result.txt")
    print("="*60)

if __name__ == "__main__":
    main()