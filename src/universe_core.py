# universe_core.py
import numpy as np
import random
import warnings
warnings.filterwarnings("ignore")

# ==================== НАСТРОЙКИ ====================
TIME_STEP = 0.02
MAX_PARTICLES = 80
# ===================================================

class Universe:
    def __init__(self, n_particles, G, Lambda, Q, crit_dist, neg_mass_ratio=0.0, noise_level=0.0001, fluct_rate=0.006):
        self.n = min(n_particles, MAX_PARTICLES)
        self.G = G
        self.Lambda = Lambda
        self.Q = Q
        self.crit_dist = crit_dist
        self.noise_level = noise_level
        self.fluct_rate = fluct_rate
        
        # Начальные условия - всё в центре
        self.pos = np.zeros((self.n, 2))
        self.vel = np.zeros((self.n, 2))
        
        # Массы
        self.mass = np.ones(self.n)
        n_neg = int(self.n * neg_mass_ratio)
        if n_neg > 0:
            self.mass[:n_neg] = -0.5
        
        # Статистика
        self.time = 0
        self.size_history = []
        self.entropy_history = []
        self.spectrum_history = []
        self.max_history = 500
        self.cycle_count = 0
        self.last_cycle_time = 0
        self.big_fluctuation_count = 0
        
    def compute_forces(self):
        n = self.n
        forces = np.zeros((n, 2))
        epsilon = 1e-5
        
        for i in range(n):
            for j in range(i+1, n):
                r = self.pos[j] - self.pos[i]
                dist = np.linalg.norm(r) + epsilon
                
                direction = r / dist
                
                F_grav = -self.G * self.mass[i] * self.mass[j] / (dist**2)
                
                F_quantum = 0
                if dist < self.crit_dist and abs(self.Q) > 1e-10:
                    F_quantum = +self.Q / (dist**4)
                
                F_dark = self.Lambda * dist
                
                total_force = F_grav + F_quantum + F_dark
                
                forces[i] += total_force * direction
                forces[j] -= total_force * direction
        
        for i in range(n):
            mass_abs = abs(self.mass[i])
            if mass_abs < epsilon:
                mass_abs = epsilon
            forces[i] /= mass_abs
        
        return forces
    
    def compute_spectrum(self):
        """Вычисляет спектр мощности по распределению частиц"""
        active = np.where(np.isfinite(self.pos[:,0]))[0]
        if len(active) < 2:
            return None, None
        
        pos = self.pos[active]
        r = np.linalg.norm(pos, axis=1)
        
        if len(r) < 2:
            return None, None
        
        # Гистограмма с фиксированным числом бинов
        hist, bins = np.histogram(r, bins=10, density=False)
        centers = (bins[:-1] + bins[1:]) / 2
        
        # Нормируем вручную
        if np.sum(hist) > 0:
            hist = hist / np.sum(hist)
        else:
            return None, None
        
        return centers, hist
    
    def step(self):
        forces = self.compute_forces()
        
        # Метод Верле
        self.vel += forces * TIME_STEP * 0.5
        self.pos += self.vel * TIME_STEP
        forces_new = self.compute_forces()
        self.vel += forces_new * TIME_STEP * 0.5
        
        # Квантовый шум
        if self.noise_level > 0:
            self.vel += np.random.randn(self.n, 2) * self.noise_level
        
        # Большая флуктуация
        if random.random() < self.fluct_rate:
            fluct_strength = random.uniform(0.5, 2.0)
            self.vel += np.random.randn(self.n, 2) * fluct_strength
            self.big_fluctuation_count += 1
            # print(f"⚡ ФЛУКТУАЦИЯ #{self.big_fluctuation_count}")  # закомментил для фона
        
        # Мягкое центрирование
        center = np.mean(self.pos, axis=0)
        self.pos -= center * 0.0001
        
        # Размер
        current_size = np.std(self.pos)
        if np.isnan(current_size) or np.isinf(current_size):
            current_size = 0
        
        # Энтропия (разброс скоростей)
        speeds = np.linalg.norm(self.vel, axis=1)
        current_entropy = np.mean(speeds)
        if np.isnan(current_entropy) or np.isinf(current_entropy):
            current_entropy = 0
        
        # Проверка на новый цикл
        if len(self.size_history) > 20:
            old_size = np.mean(self.size_history[-20:])
            if current_size > old_size * 1.8 and self.time - self.last_cycle_time > 50:
                self.cycle_count += 1
                self.last_cycle_time = self.time
                # print(f"🔄 НОВЫЙ ЦИКЛ #{self.cycle_count}!")  # закомментил
        
        self.time += TIME_STEP
        self.size_history.append(current_size)
        self.entropy_history.append(current_entropy)
        
        if len(self.size_history) > self.max_history:
            self.size_history.pop(0)
            self.entropy_history.pop(0)