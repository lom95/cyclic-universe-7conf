#!/usr/bin/env python3
"""
Entry point for the cyclic universe project with negative mass.
Allows running simulation or individual confirmations.
"""

import sys
import os
import argparse
import subprocess

# Add root directory to Python path
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT_DIR)

def print_header():
    """Prints header"""
    print("="*60)
    print("CYCLIC UNIVERSE WITH NEGATIVE MASS")
    print("7 CONFIRMATIONS")
    print("="*60)

def get_script_path(script_name):
    """Returns full path to script in scripts/ folder"""
    return os.path.join(ROOT_DIR, "scripts", script_name)

def check_scripts():
    """Check if all required scripts exist"""
    scripts_dir = os.path.join(ROOT_DIR, "scripts")
    required = [
        'fit_scale_factor.py',
        'fit_entropy.py',
        'cmb_check.py',
        'sdss_check.py',
        'mcxc_check.py',
        'gamma_dipole.py',
        'bao_analysis_fixed.py',
        'supernova_confirmation_final.py',
        'h0_confirmation.py'
    ]
    
    print("\nChecking scripts folder...")
    all_found = True
    for script in required:
        path = os.path.join(scripts_dir, script)
        if os.path.exists(path):
            print(f"  [OK] {script}")
        else:
            print(f"  [MISSING] {script}")
            all_found = False
    return all_found

def run_simulation():
    """Runs the visual simulation"""
    print("\nStarting universe simulation...")
    try:
        sys.path.insert(0, os.path.join(ROOT_DIR, "src"))
        from src.universe_visual import main
        main()
    except Exception as e:
        print(f"Error: {e}")

def run_confirmation(conf_number):
    """Runs a specific confirmation by number"""
    confirmations = {
        '1': ('Scale factor', 'fit_scale_factor.py'),
        '2': ('Entropy', 'fit_entropy.py'),
        '3': ('CMB (1st)', 'cmb_check.py'),
        '4': ('SDSS (2nd)', 'sdss_check.py'),
        '5': ('MCXC (3rd)', 'mcxc_check.py'),
        '6': ('Gamma dipole (4th)', 'gamma_dipole.py'),
        '7': ('BAO (5th)', 'bao_analysis_fixed.py'),
        '8': ('Supernovae (6th)', 'supernova_confirmation_final.py'),
        '9': ('H₀ (7th)', 'h0_confirmation.py'),
        'all': ('All confirmations', 'run_all_confirmations.py')
    }
    
    if conf_number not in confirmations:
        print(f"Invalid choice. Available: {', '.join(confirmations.keys())}")
        return False
    
    name, script = confirmations[conf_number]
    script_path = get_script_path(script)
    
    print(f"\nRunning: {name}")
    print(f"Script: {script_path}")
    
    if not os.path.exists(script_path):
        print(f"Error: {script_path} not found!")
        return False
    
    try:
        result = subprocess.run([sys.executable, script_path], 
                               cwd=ROOT_DIR,
                               capture_output=True, 
                               text=True)
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print("Warnings:")
            print(result.stderr)
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False

def show_info():
    """Shows model information"""
    print("\nMODEL INFORMATION")
    print("-" * 40)
    print("""
MODEL: Cyclic Universe with Negative Mass (-M)

KEY FEATURES:
• Quantum bounce instead of singularity
• Negative mass (-M) explains dark matter
• Cycle memory through -M
• Entropy reset at bounce

7 CONFIRMATIONS:
1. CMB (Planck) - first peaks ✓
2. SDSS - large-scale structure ✓
3. MCXC - galaxy clusters ✓
4. Gamma-ray dipole (Fermi) ✓
5. BAO - peak at 150 Mpc ✓
6. Type Ia supernovae ✓
7. H₀ = 79.93 ± 2.74 km/s/Mpc ✓

SOLVED PROBLEMS (13):
• Singularity • Entropy • Dark matter
• Gamma dipole • Time • Cycles
    """)

def main():
    parser = argparse.ArgumentParser(description='Cyclic Universe with -M')
    parser.add_argument('mode', nargs='?', default='menu',
                        choices=['sim', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'all', 'info', 'menu', 'check'],
                        help='run mode')
    
    args = parser.parse_args()
    
    if args.mode == 'menu':
        print_header()
        check_scripts()
        
        while True:
            print("\nAVAILABLE MODES:")
            print("  [0] - Run simulation")
            print("  [1] - Scale factor")
            print("  [2] - Entropy")
            print("  [3] - CMB (1st confirmation)")
            print("  [4] - SDSS (2nd confirmation)")
            print("  [5] - MCXC (3rd confirmation)")
            print("  [6] - GAMMA DIPOLE (4th confirmation)")
            print("  [7] - BAO (5th confirmation)")
            print("  [8] - Supernovae (6th confirmation)")
            print("  [9] - H₀ (7th confirmation)")
            print("  [a] - ALL confirmations")
            print("  [i] - Model info")
            print("  [q] - Quit")
            
            choice = input("\nChoose mode: ").strip().lower()
            
            if choice == 'q':
                break
            elif choice == '0':
                run_simulation()
            elif choice == '1':
                run_confirmation('1')
            elif choice == '2':
                run_confirmation('2')
            elif choice == '3':
                run_confirmation('3')
            elif choice == '4':
                run_confirmation('4')
            elif choice == '5':
                run_confirmation('5')
            elif choice == '6':
                run_confirmation('6')
            elif choice == '7':
                run_confirmation('7')
            elif choice == '8':
                run_confirmation('8')
            elif choice == '9':
                run_confirmation('9')
            elif choice == 'a':
                run_confirmation('all')
            elif choice == 'i':
                show_info()
            else:
                print("Invalid choice")
            
            input("\nPress Enter to continue...")
    
    elif args.mode == 'sim':
        run_simulation()
    elif args.mode == 'info':
        show_info()
    elif args.mode == 'check':
        check_scripts()
    elif args.mode in ['1', '2', '3', '4', '5', '6', '7', '8', '9', 'all']:
        run_confirmation(args.mode)
    else:
        print("Unknown mode. Use: python run.py menu")

if __name__ == "__main__":
    main()