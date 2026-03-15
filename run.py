#!/usr/bin/env python3
"""
Точка входа в проект циклической Вселенной с отрицательной массой.
Запускает симуляцию или анализ подтверждений.
"""

import sys
import os
import argparse

# Добавляем корневую папку в путь поиска модулей
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def print_header():
    """Выводит красивый заголовок"""
    print("""
    ╔══════════════════════════════════════════════════════════╗
    ║     ЦИКЛИЧЕСКАЯ ВСЕЛЕННАЯ С ОТРИЦАТЕЛЬНОЙ МАССОЙ         ║
    ║                   7 ПОДТВЕРЖДЕНИЙ                        ║
    ╚══════════════════════════════════════════════════════════╝
    """)

def run_simulation():
    """Запускает визуальную симуляцию"""
    print("🚀 Запуск симуляции Вселенной...")
    try:
        from src.universe_visual import main
        main()
    except ImportError as e:
        print(f"❌ Ошибка импорта: {e}")
        print("   Убедись, что файл src/universe_visual.py существует")
    except Exception as e:
        print(f"❌ Ошибка при запуске симуляции: {e}")

def run_analysis(analysis_type):
    """Запускает различные виды анализа"""
    
    if analysis_type == 'scale':
        print("📊 Анализ масштабного фактора...")
        from scripts.fit_scale_factor import main
        main()
    
    elif analysis_type == 'entropy':
        print("📊 Анализ энтропии...")
        from scripts.fit_entropy import main
        main()
    
    elif analysis_type == 'bao':
        print("📊 Анализ BAO...")
        from scripts.bao_analysis import main
        main()
    
    elif analysis_type == 'supernova':
        print("📊 Подтверждение 6: Сверхновые Ia...")
        from scripts.supernova_confirmation import main
        main()
    
    elif analysis_type == 'h0':
        print("📊 Подтверждение 7: Постоянная Хаббла H₀...")
        from scripts.h0_confirmation import main
        main()
    
    elif analysis_type == 'all':
        print("📊 Запуск всех анализов...")
        from scripts.fit_scale_factor import main as scale_main
        from scripts.fit_entropy import main as entropy_main
        from scripts.bao_analysis import main as bao_main
        from scripts.supernova_confirmation import main as supernova_main
        from scripts.h0_confirmation import main as h0_main
        
        scale_main()
        print("\n" + "="*50 + "\n")
        entropy_main()
        print("\n" + "="*50 + "\n")
        bao_main()
        print("\n" + "="*50 + "\n")
        supernova_main()
        print("\n" + "="*50 + "\n")
        h0_main()
    
    else:
        print(f"❌ Неизвестный тип анализа: {analysis_type}")

def show_confirmations():
    """Показывает список подтверждений"""
    print("\n📋 ПОДТВЕРЖДЕНИЯ МОДЕЛИ:\n")
    confirmations = [
        "1. CMB (Planck) - первые пики спектра",
        "2. SDSS - крупномасштабная структура",
        "3. MCXC - скопления галактик",
        "4. Гамма-диполь (Fermi) - направление анизотропии",
        "5. BAO - барионные акустические осцилляции",
        "6. Сверхновые Ia - модуль расстояния μ(z)",
        "7. Постоянная Хаббла H₀ = 79.93 ± 2.74"
    ]
    
    for i, conf in enumerate(confirmations, 1):
        print(f"   {conf}")

def main():
    """Главная функция"""
    parser = argparse.ArgumentParser(description='Циклическая Вселенная с -M')
    parser.add_argument('mode', nargs='?', default='sim',
                        choices=['sim', 'scale', 'entropy', 'bao', 'supernova', 'h0', 'all', 'info'],
                        help='режим запуска (sim - симуляция, info - информация)')
    
    args = parser.parse_args()
    
    print_header()
    
    if args.mode == 'info':
        show_confirmations()
        print("\n📌 Доступные режимы:")
        print("   sim       - запуск симуляции")
        print("   scale     - анализ масштабного фактора")
        print("   entropy   - анализ энтропии")
        print("   bao       - анализ BAO")
        print("   supernova - анализ сверхновых (6-е подтверждение)")
        print("   h0        - анализ H₀ (7-е подтверждение)")
        print("   all       - все анализы подряд")
        print("   info      - эта информация")
    
    elif args.mode == 'sim':
        run_simulation()
    
    elif args.mode in ['scale', 'entropy', 'bao', 'supernova', 'h0', 'all']:
        run_analysis(args.mode)
    
    else:
        print("❌ Неизвестный режим. Используй: python run.py info")

if __name__ == "__main__":
    main()