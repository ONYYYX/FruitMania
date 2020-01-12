import math
import pygame
import vendor.padlib.particles as particles
import singletons
import sprites
import config


class Blade(pygame.sprite.Sprite):
    def __init__(self, *groups):
        super().__init__(singletons.BladesGroup.get(), *groups)
        self._session_started = False
        self.rect = pygame.Rect(0, 0, *config.blade_size)
        self.cut_fruits = []
        self.mouse_track = []
        self.emitter = self.set_emitter()
        self.particle_system = self.set_particle_system()

    @property
    def session_started(self):
        return self._session_started

    @session_started.setter
    def session_started(self, value):
        if not value:
            self.check_combo()
        self.cut_fruits.clear()
        self.mouse_track.clear()
        self._session_started = value

    def check_combo(self):
        max_combo = self.get_max_combo()
        if max_combo >= 1:
            sprites.CenteredFruitScore(f'Combo {max_combo + 2} fruits', max_combo * 2)
            pygame.mixer.Sound(f'media/sounds/combo-{max_combo if max_combo <= 8 else 8}.ogg').play()

    def get_max_combo(self):
        curvatures = []
        for i in range(len(self.cut_fruits) - 2):
            curvatures.append(self.get_curvature([list(self.cut_fruits[j]) for j in range(i, i + 3)]))
        current_combo_num = 0
        combo_nums = []
        for c in curvatures:
            if c <= 125:
                current_combo_num += 1
            else:
                combo_nums.append(current_combo_num)
                current_combo_num = 0
        combo_nums.append(current_combo_num)
        max_combo = 0
        if combo_nums:
            max_combo += max(combo_nums)
        return max_combo

    def get_curvature(self, points):
        # Находим "кривизну" нашей ломаной в средней точке (собственный алгоритм, кривой мб)
        # Алгоритм:
        # Для каждой тройки точек:
        # Делим удвоенную площадь треугольника на расстояние между крайними точками
        # Это и будет "кривизна" (высота треугольника) в пикселях
        # Ищем наибольшую "кривизну", если не больше 50px, то ломаная - относительно прямая линия
        triangle_base = math.sqrt((points[2][0] - points[0][0]) ** 2 + (points[2][1] - points[0][1]) ** 2)
        if triangle_base:
            return abs(
                (points[2][1] - points[0][1]) * points[1][0] - (points[2][0] - points[0][0]) * points[1][1] +
                points[2][0] * points[0][1] - points[2][1] * points[0][0]
            ) / triangle_base
        else:
            return 1

    def add_cut_fruit(self, fruit):
        x, y = fruit.rect.x, fruit.rect.y
        self.cut_fruits.append((x + fruit.rect.w // 2, y + fruit.rect.h // 2))
        fruit.cut()

    def add_mouse_track_pos(self, pos):
        self.mouse_track.append(pos)

    def set_emitter(self):
        emitter = particles.Emitter()
        emitter.set_density(100)
        emitter.set_angle(0.0, 180.0)
        emitter.set_speed([30.0, 100.0])
        emitter.set_life([0.5, 1.0])
        emitter.set_colors([(255, 0, 0), (255, 255, 0), (0, 255, 0), (0, 255, 255), (0, 0, 255), (0, 0, 0)])
        return emitter

    def set_particle_system(self):
        particle_system = particles.ParticleSystem()
        particle_system.set_particle_acceleration([0.0, 100.0])
        particle_system.add_emitter(self.emitter, "emitter")
        return particle_system

    def create_particles(self, surface):
        self.emitter.set_position((self.rect.x, self.rect.y) if pygame.mouse.get_pressed()[0] else (9999, 9999))
        self.particle_system.draw(surface)
        self.particle_system.update(1.0 / config.fps)

    def update(self, *args):
        self.rect.x, self.rect.y = pygame.mouse.get_pos()
        self.create_particles(args[0])

