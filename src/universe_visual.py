import pygame
import numpy as np
import sys
import warnings
import random
import matplotlib.pyplot as plt
import os
warnings.filterwarnings("ignore")

# ==================== НАСТРОЙКИ ====================
WIDTH, HEIGHT = 1200, 700
FPS = 60
TIME_STEP = 0.02
MAX_PARTICLES = 80
BH_DENSITY_THRESHOLD = 1
BH_MASS_FACTOR = 0.01
BLACK_HOLE_FORMATION_TIME = 30.0
# ===================================================

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Циклическая Вселенная - С расширением")
clock = pygame.time.Clock()
font = pygame.font.SysFont('Arial', 16)
input_font = pygame.font.SysFont('Arial', 20)

# Цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 80, 80)
GREEN = (80, 255, 80)
BLUE = (80, 80, 255)
GRAY = (120, 120, 120)
DARK_GRAY = (40, 40, 40)
YELLOW = (255, 255, 80)
PURPLE = (200, 80, 255)
ORANGE = (255, 160, 80)
CYAN = (80, 255, 255)

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
        
        # ===== МАСШТАБНЫЙ ФАКТОР =====
        self.scale_factor = 1.0
        self.scale_factor_dot = 0.0
        self.scale_factor_history = []
        
        # ===== АВТОМАТИЧЕСКОЕ СОХРАНЕНИЕ =====
        os.makedirs("scale_factor_data", exist_ok=True)
        
        # Файл для масштабного фактора
        self.scale_factor_file = open(f"scale_factor_data/scale_factor_{id(self)}.txt", "w")
        self.scale_factor_file.write("# time scale_factor\n")
        
        # Файл для полных данных (время, a, энтропия)
        self.data_file = open("simulation_data.txt", "w")
        self.data_file.write("# time scale_factor entropy\n")
        # =======================================
        
        # ===== ЧЁРНЫЕ ДЫРЫ =====
        self.is_black_hole = np.zeros(self.n, dtype=bool)
        self.bh_mass = np.zeros(self.n)
        self.bh_merge_count = 0
        self.bh_events = []
        self.black_hole_formation_time = BLACK_HOLE_FORMATION_TIME
        # ================================
        
        # Статистика
        self.time = 0
        self.size_history = []
        self.entropy_history = []
        self.spectrum_history = []
        self.max_history = 500
        self.cycle_count = 0
        self.last_cycle_time = 0
        self.big_fluctuation_count = 0
    
    def __del__(self):
        """Закрываем файлы при удалении объекта"""
        if hasattr(self, 'scale_factor_file'):
            self.scale_factor_file.close()
        if hasattr(self, 'data_file'):
            self.data_file.close()
            print("💾 Данные сохранены в simulation_data.txt")
    
    def save_cycle_data(self):
        """Сохраняет данные отдельно для каждого цикла"""
        if len(self.scale_factor_history) > 0:
            cycle_filename = f"scale_factor_data/cycle_{self.cycle_count}_time_{int(self.time)}.txt"
            with open(cycle_filename, 'w') as f:
                f.write("# time scale_factor\n")
                for i, val in enumerate(self.scale_factor_history):
                    f.write(f"{i * TIME_STEP:.6f} {val:.6f}\n")
            print(f"💾 Данные цикла #{self.cycle_count} сохранены")
    
    def compute_forces(self):
        n = self.n
        forces = np.zeros((n, 2))
        epsilon = 1e-5
        
        for i in range(n):
            for j in range(i+1, n):
                r = self.pos[j] - self.pos[i]
                dist = np.linalg.norm(r) + epsilon
                
                direction = r / dist
                
                # Гравитация
                mass_i = self.bh_mass[i] if self.is_black_hole[i] else self.mass[i]
                mass_j = self.bh_mass[j] if self.is_black_hole[j] else self.mass[j]
                F_grav = -self.G * mass_i * mass_j / (dist**2)
                
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
    
    def update_scale_factor(self):
        """Масштабный фактор следует за размером Вселенной"""
        current_size = np.std(self.pos)
        if current_size < 0.01:
            current_size = 0.01
        
        target_scale = current_size * 2.0
        self.scale_factor = self.scale_factor * 0.95 + target_scale * 0.05
        
        self.scale_factor_history.append(self.scale_factor)
        if len(self.scale_factor_history) > self.max_history:
            self.scale_factor_history.pop(0)
        
        self.scale_factor_file.write(f"{self.time:.6f} {self.scale_factor:.6f}\n")
        self.scale_factor_file.flush()
        
        self.scale_factor_dot = (self.scale_factor - self.scale_factor_history[-2]) / TIME_STEP if len(self.scale_factor_history) > 1 else 0
        return self.scale_factor_dot / self.scale_factor if self.scale_factor > 0 else 0
    
    def check_black_hole_formation(self):
        if self.time < self.black_hole_formation_time:
            return
        
        for i in range(self.n):
            if self.is_black_hole[i]:
                continue
            
            neighbors = 0
            for j in range(self.n):
                if i == j:
                    continue
                dist = np.linalg.norm(self.pos[i] - self.pos[j])
                if dist < 5:
                    neighbors += 1
            
            if neighbors > BH_DENSITY_THRESHOLD:
                self.is_black_hole[i] = True
                self.bh_mass[i] = abs(self.mass[i]) * neighbors * BH_MASS_FACTOR
                print(f"🕳️ Чёрная дыра! Частица {i}, время {self.time:.2f}")
    
    def check_black_hole_mergers(self):
        for i in range(self.n):
            if not self.is_black_hole[i]:
                continue
            
            for j in range(i+1, self.n):
                if not self.is_black_hole[j]:
                    continue
                
                dist = np.linalg.norm(self.pos[i] - self.pos[j])
                if dist < 0.01:
                    new_mass = self.bh_mass[i] + self.bh_mass[j]
                    print(f"💥 СЛИЯНИЕ! {self.bh_mass[i]:.2f} + {self.bh_mass[j]:.2f} = {new_mass:.2f}")
                    
                    self.bh_events.append({
                        'time': self.time,
                        'mass1': self.bh_mass[i],
                        'mass2': self.bh_mass[j],
                        'mass_total': new_mass
                    })
                    self.bh_merge_count += 1
                    
                    self.bh_mass[i] = new_mass
                    self.is_black_hole[j] = False
                    self.mass[j] = 0.1
    
    def compute_spectrum(self):
        active = np.where(np.isfinite(self.pos[:,0]))[0]
        if len(active) < 2:
            return None, None
        
        pos = self.pos[active]
        r = np.linalg.norm(pos, axis=1)
        
        if len(r) < 2:
            return None, None
        
        hist, bins = np.histogram(r, bins=10, density=False)
        centers = (bins[:-1] + bins[1:]) / 2
        
        if np.sum(hist) > 0:
            hist = hist / np.sum(hist)
        else:
            return None, None
        
        return centers, hist
    
    def step(self):
        # Силы гравитации
        forces = self.compute_forces()
        
        # Метод Верле
        self.vel += forces * TIME_STEP * 0.5
        self.pos += self.vel * TIME_STEP
        forces_new = self.compute_forces()
        self.vel += forces_new * TIME_STEP * 0.5
        
        # Обновление масштабного фактора
        H = self.update_scale_factor()
        
        # Квантовый шум
        if self.noise_level > 0:
            self.vel += np.random.randn(self.n, 2) * self.noise_level
        
        # Большая флуктуация
        if random.random() < self.fluct_rate:
            fluct_strength = random.uniform(0.5, 2.0)
            self.vel += np.random.randn(self.n, 2) * fluct_strength
            self.big_fluctuation_count += 1
            print(f"⚡ ФЛУКТУАЦИЯ #{self.big_fluctuation_count}")
        
        # Мягкое центрирование
        center = np.mean(self.pos, axis=0)
        self.pos -= center * 0.0001
        
        # Чёрные дыры
        self.check_black_hole_formation()
        self.check_black_hole_mergers()
        
        # Размер и энтропия
        current_size = np.std(self.pos)
        if np.isnan(current_size) or np.isinf(current_size):
            current_size = 0
        
        speeds = np.linalg.norm(self.vel, axis=1)
        current_entropy = np.mean(speeds)
        if np.isnan(current_entropy) or np.isinf(current_entropy):
            current_entropy = 0
        
        # ===== СОХРАНЯЕМ ПОЛНЫЕ ДАННЫЕ =====
        self.data_file.write(f"{self.time:.6f} {self.scale_factor:.6f} {current_entropy:.6f}\n")
        self.data_file.flush()
        # ====================================
        
        # Проверка на новый цикл
        if len(self.size_history) > 20:
            old_size = np.mean(self.size_history[-20:])
            if current_size > old_size * 1.8 and self.time - self.last_cycle_time > 50:
                self.cycle_count += 1
                self.last_cycle_time = self.time
                print(f"🔄 НОВЫЙ ЦИКЛ #{self.cycle_count}!")
                
                self.save_cycle_data()
                
                filename = f"positions_cycle_{self.cycle_count}.txt"
                np.savetxt(filename, self.pos, header='x y', fmt='%.6f')
                
                centers, hist = self.compute_spectrum()
                if centers is not None:
                    self.spectrum_history.append((centers, hist))
                    filename_spec = f"spectrum_cycle_{self.cycle_count}.txt"
                    np.savetxt(filename_spec, np.column_stack((centers, hist)), 
                               header=f"Cycle {self.cycle_count}\nradius density", 
                               fmt='%.6f')
                
                if len(self.bh_events) > 0:
                    ligo_filename = f"ligo_events_cycle_{self.cycle_count}.txt"
                    with open(ligo_filename, 'w') as f:
                        f.write("# time mass1 mass2 mass_total\n")
                        for ev in self.bh_events:
                            f.write(f"{ev['time']:.2f} {ev['mass1']:.2f} {ev['mass2']:.2f} {ev['mass_total']:.2f}\n")
        
        self.time += TIME_STEP
        self.size_history.append(current_size)
        self.entropy_history.append(current_entropy)
        
        if len(self.size_history) > self.max_history:
            self.size_history.pop(0)
            self.entropy_history.pop(0)
            self.scale_factor_history.pop(0)
    
    def get_display_positions(self):
        pos_clean = np.nan_to_num(self.pos, nan=0.0)
        
        min_x, max_x = np.min(pos_clean[:, 0]), np.max(pos_clean[:, 0])
        min_y, max_y = np.min(pos_clean[:, 1]), np.max(pos_clean[:, 1])
        
        range_x = max(max_x - min_x, 0.5)
        range_y = max(max_y - min_y, 0.5)
        
        scale_x = (WIDTH - 300) / range_x
        scale_y = HEIGHT / range_y
        scale = min(scale_x, scale_y) * 0.8
        
        center_x = (min_x + max_x) / 2
        center_y = (min_y + max_y) / 2
        
        pos_centered = pos_clean - [center_x, center_y]
        
        result = (pos_centered * scale + [(WIDTH - 300)//2, HEIGHT//2]).astype(int)
        return result

class InputBox:
    def __init__(self, x, y, w, h, text='', label='', is_float=True):
        self.rect = pygame.Rect(x, y, w, h)
        self.color = GRAY
        self.text = text
        self.label = label
        self.active = False
        self.value = 0.0
        self.is_float = is_float
        try:
            self.value = float(text) if text else 0.0
        except:
            self.value = 0.0
        
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
            self.color = BLUE if self.active else GRAY
            
        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_RETURN:
                try:
                    self.value = float(self.text) if self.text else 0.0
                except:
                    pass
                self.active = False
                self.color = GRAY
            elif event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.key == pygame.K_ESCAPE:
                self.active = False
                self.color = GRAY
            else:
                if self.is_float:
                    if event.unicode.isdigit() or event.unicode == '.' or (event.unicode == '-' and len(self.text) == 0):
                        self.text += event.unicode
                else:
                    if event.unicode.isdigit():
                        self.text += event.unicode
    
    def get_value(self):
        try:
            return float(self.text) if self.text else self.value
        except:
            return self.value
                
    def draw(self, screen):
        pygame.draw.rect(screen, BLACK, self.rect)
        border = 3 if self.active else 2
        pygame.draw.rect(screen, self.color, self.rect, border)
        
        display_text = self.text if self.text else f"{self.value:.4f}" if self.is_float else str(int(self.value))
        if len(display_text) > 10:
            display_text = display_text[:10]
        text_surface = input_font.render(display_text, True, WHITE)
        screen.blit(text_surface, (self.rect.x + 5, self.rect.y + 5))
        
        label_surface = font.render(self.label, True, WHITE)
        screen.blit(label_surface, (self.rect.x, self.rect.y - 18))

# Поля ввода
input_boxes = [
    InputBox(20, 70, 100, 30, '50', 'Частицы', is_float=False),
    InputBox(20, 140, 100, 30, '0.1', 'G'),
    InputBox(20, 210, 100, 30, '0.05', 'Λ'),
    InputBox(20, 280, 100, 30, '0.02', 'Q'),
    InputBox(20, 350, 100, 30, '0.02', 'R_crit'),
    InputBox(20, 420, 100, 30, '5', '-M %'),
    InputBox(20, 490, 100, 30, '0.0001', 'Шум'),
    InputBox(140, 70, 100, 30, '0.006', 'Флукт.'),
]

# Кнопки
buttons = [
    {"rect": pygame.Rect(260, 560, 100, 40), "text": "СТАРТ", "color": GREEN},
    {"rect": pygame.Rect(380, 560, 100, 40), "text": "СБРОС", "color": BLUE},
    {"rect": pygame.Rect(500, 560, 150, 40), "text": "LIGO", "color": RED},
]

# Состояние
universe = None
running = True
pause = False
simulation_active = False

while running:
    dt = clock.tick(FPS)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
        for box in input_boxes:
            box.handle_event(event)
            
        if event.type == pygame.MOUSEBUTTONDOWN:
            if buttons[0]["rect"].collidepoint(event.pos):
                try:
                    n = int(input_boxes[0].text) if input_boxes[0].text else 50
                    G = float(input_boxes[1].text) if input_boxes[1].text else 0.1
                    Lambda = float(input_boxes[2].text) if input_boxes[2].text else 0.05
                    Q = float(input_boxes[3].text) if input_boxes[3].text else 0.02
                    crit_dist = float(input_boxes[4].text) if input_boxes[4].text else 0.02
                    neg_ratio = float(input_boxes[5].text) if input_boxes[5].text else 5.0
                    noise = float(input_boxes[6].text) if input_boxes[6].text else 0.0001
                    fluct = float(input_boxes[7].text) if input_boxes[7].text else 0.006
                    
                    universe = Universe(n, G, Lambda, Q, crit_dist, neg_ratio/100.0, noise, fluct)
                    simulation_active = True
                    pause = False
                except Exception as e:
                    print(f"Ошибка: {e}")
            
            elif buttons[1]["rect"].collidepoint(event.pos):
                if universe:
                    universe = Universe(
                        int(input_boxes[0].text),
                        float(input_boxes[1].text),
                        float(input_boxes[2].text),
                        float(input_boxes[3].text),
                        float(input_boxes[4].text),
                        float(input_boxes[5].text)/100.0,
                        float(input_boxes[6].text),
                        float(input_boxes[7].text)
                    )
            
            elif buttons[2]["rect"].collidepoint(event.pos):
                if universe and len(universe.bh_events) > 0:
                    masses1 = [e['mass1'] for e in universe.bh_events]
                    masses2 = [e['mass2'] for e in universe.bh_events]
                    times = [e['time'] for e in universe.bh_events]
                    
                    plt.figure(figsize=(12, 5))
                    
                    plt.subplot(1, 2, 1)
                    plt.hist(masses1 + masses2, bins=20, alpha=0.7, color='purple')
                    plt.xlabel('Масса чёрной дыры')
                    plt.ylabel('Количество')
                    plt.title('Распределение масс чёрных дыр')
                    plt.grid(alpha=0.3)
                    
                    plt.subplot(1, 2, 2)
                    plt.plot(times, range(len(times)), 'ro-', markersize=3)
                    plt.xlabel('Время')
                    plt.ylabel('Накопленное число слияний')
                    plt.title('Частота слияний')
                    plt.grid(alpha=0.3)
                    
                    plt.tight_layout()
                    plt.show()
                    print(f"✅ Всего слияний: {len(universe.bh_events)}")
                else:
                    print("⚠️ Нет данных о слияниях")
                    
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and simulation_active:
                pause = not pause
            elif event.key == pygame.K_ESCAPE:
                running = False
    
    # Отрисовка
    screen.fill(BLACK)
    
    for box in input_boxes:
        box.draw(screen)
    
    for button in buttons:
        pygame.draw.rect(screen, button["color"], button["rect"])
        text_surface = font.render(button["text"], True, BLACK)
        text_rect = text_surface.get_rect(center=button["rect"].center)
        screen.blit(text_surface, text_rect)
    
    if simulation_active and universe:
        if not pause:
            for _ in range(2):
                universe.step()
        
        # Рисуем частицы
        display_pos = universe.get_display_positions()
        for i, (x, y) in enumerate(display_pos):
            if 0 <= x < WIDTH and 0 <= y < HEIGHT and i < universe.n:
                if universe.is_black_hole[i]:
                    color = RED
                elif universe.mass[i] < 0:
                    color = BLUE
                else:
                    speed = np.linalg.norm(universe.vel[i])
                    brightness = min(255, int(100 + speed * 50))
                    color = (0, brightness, 0)
                screen.set_at((x, y), color)
        
        # Информация
        info_texts = [
            f"Время: {universe.time:.2f}",
            f"Масштаб a: {universe.scale_factor:.4f}",
            f"Размер: {np.std(universe.pos):.4f}",
            f"Энтропия: {np.mean(np.linalg.norm(universe.vel, axis=1)):.4f}",
            f"Циклов: {universe.cycle_count}",
            f"Чёрных дыр: {np.sum(universe.is_black_hole)}",
            f"Слияний: {universe.bh_merge_count}",
            f"Флуктуаций: {universe.big_fluctuation_count}",
            f"Пауза: {'ДА' if pause else 'НЕТ'}",
        ]
        
        for i, text in enumerate(info_texts):
            surface = font.render(text, True, WHITE)
            screen.blit(surface, (20, 550 + i * 18))
        
        # График размера
        if len(universe.size_history) > 5:
            graph_x = WIDTH - 280
            graph_y = 50
            graph_w = 250
            graph_h = 150
            
            pygame.draw.rect(screen, DARK_GRAY, (graph_x, graph_y, graph_w, graph_h), 2)
            
            hist = universe.size_history[-graph_w:]
            
            if len(hist) > 2:
                max_val = max(hist)
                min_val = min(hist)
                range_val = max_val - min_val if max_val > min_val else 1
                
                points = []
                for i, val in enumerate(hist):
                    x = graph_x + (i * graph_w // len(hist))
                    y = graph_y + graph_h - int((val - min_val) / range_val * (graph_h - 20)) - 10
                    points.append((x, y))
                
                if len(points) > 1:
                    pygame.draw.lines(screen, GREEN, False, points, 2)
            
            graph_label = font.render("Размер", True, WHITE)
            screen.blit(graph_label, (graph_x + 10, graph_y - 20))
        
        # График масштабного фактора
        if len(universe.scale_factor_history) > 5:
            scale_x = WIDTH - 280
            scale_y = 220
            scale_w = 250
            scale_h = 80
            
            pygame.draw.rect(screen, DARK_GRAY, (scale_x, scale_y, scale_w, scale_h), 1)
            
            hist = universe.scale_factor_history[-scale_w:]
            if len(hist) > 2:
                max_val = max(hist)
                min_val = min(hist)
                range_val = max_val - min_val if max_val > min_val else 1
                
                points = []
                for i, val in enumerate(hist):
                    x = scale_x + (i * scale_w // len(hist))
                    y = scale_y + scale_h - int((val - min_val) / range_val * (scale_h - 10)) - 5
                    points.append((x, y))
                
                if len(points) > 1:
                    pygame.draw.lines(screen, CYAN, False, points, 2)
            
            scale_label = font.render("Масштаб a(t)", True, WHITE)
            screen.blit(scale_label, (scale_x, scale_y - 18))
        
        # График энтропии
        if len(universe.entropy_history) > 5:
            ent_x = WIDTH - 280
            ent_y = 320
            ent_w = 250
            ent_h = 60
            
            pygame.draw.rect(screen, DARK_GRAY, (ent_x, ent_y, ent_w, ent_h), 1)
            
            hist = universe.entropy_history[-ent_w:]
            if len(hist) > 2:
                max_val = max(hist)
                min_val = min(hist)
                range_val = max_val - min_val if max_val > min_val else 1
                
                points = []
                for i, val in enumerate(hist):
                    x = ent_x + (i * ent_w // len(hist))
                    y = ent_y + ent_h - int((val - min_val) / range_val * (ent_h - 10)) - 5
                    points.append((x, y))
                
                if len(points) > 1:
                    pygame.draw.lines(screen, YELLOW, False, points, 2)
            
            ent_label = font.render("Энтропия", True, WHITE)
            screen.blit(ent_label, (ent_x, ent_y - 18))
    
    pygame.display.flip()

pygame.quit()
sys.exit()
