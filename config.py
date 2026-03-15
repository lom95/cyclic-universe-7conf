# config.py
import os

# Корневая папка проекта
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# === ПУТИ К ДАННЫМ ===
DATA_DIR = os.path.join(BASE_DIR, "data")

# Planck
PLANCK_DIR = os.path.join(DATA_DIR, "planck")
PLANCK_FILE = os.path.join(PLANCK_DIR, "COM_PowerSpect_CMB-base-plikHM-TTTEEE-lowl-lowE-lensing-minimum-theory_R3.01.txt")

# SDSS (если есть)
SDSS_DIR = os.path.join(DATA_DIR, "sdss")
SDSS_FILE = os.path.join(SDSS_DIR, "galaxies.csv")

# MCXC (скопления)
MCXC_DIR = os.path.join(DATA_DIR, "mcxc")
MCXC_FILE = os.path.join(MCXC_DIR, "mcxcii.vot")

# === ПУТИ К РЕЗУЛЬТАТАМ ===
RESULTS_DIR = os.path.join(BASE_DIR, "results")
SCAN_RESULTS_DIR = os.path.join(RESULTS_DIR, "scan_results_full")  # твои 139 папок
BEST_DIR = os.path.join(RESULTS_DIR, "best")

# === ПУТИ К ГРАФИКАМ ===
PLOTS_DIR = os.path.join(BASE_DIR, "plots")

# === ПУТИ К ИСХОДНОМУ КОДУ ===
SRC_DIR = os.path.join(BASE_DIR, "src")
SCRIPTS_DIR = os.path.join(BASE_DIR, "scripts")

# === ПАРАМЕТРЫ ЛУЧШЕГО ЗАПУСКА ===
BEST_GAMMA = {
    'Q': 0.0102,
    'fluct': 0.007,
    'run': 0,
    'l': 176.9,
    'b': -7.3,
    'target_l': 150,
    'target_b': -5
}

# Создаём папки, если их нет
for directory in [RESULTS_DIR, SCAN_RESULTS_DIR, BEST_DIR, PLOTS_DIR]:
    os.makedirs(directory, exist_ok=True)