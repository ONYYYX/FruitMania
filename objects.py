import math
import random
import pygame
import utils
import config


class Entity(pygame.sprite.Sprite):
    image: pygame.Surface = 0
    sprite_rect = pygame.Rect((0, 0, 0, 0))

    def __init__(self, *groups):
        super().__init__(*groups)
        self.image = self.get_image()
        self.rect = self.image.get_rect()
        self._velocity = (0, 0)
        self._personal_gravity = -1

    @property
    def velocity(self):
        x, y = self._velocity
        if config.freeze_gravity:
            divider = config.gravity / config.freeze_gravity
            x = math.ceil(x / divider)
            y = math.ceil(y / divider)
        return x, y

    @velocity.setter
    def velocity(self, value):
        x, y = value
        if config.freeze_gravity:
            divider = config.gravity // config.freeze_gravity
            x *= divider
            y *= divider
        self._velocity = x, y

    @property
    def personal_gravity(self):
        return self._personal_gravity

    @personal_gravity.setter
    def personal_gravity(self, value):
        self._personal_gravity = value

    def move(self, offset):
        x, y = offset
        self.rect.x += x
        self.rect.y += y

    def update(self, *args):
        gravity = self.personal_gravity if self.personal_gravity != -1 else self.get_gravity()
        x_velocity, y_velocity = self.velocity
        self.move((self.get_frame_speed(x_velocity), self.get_frame_speed(y_velocity)))
        self.velocity = (x_velocity, y_velocity + gravity)

    @classmethod
    def get_gravity(cls):
        return config.gravity if not config.freeze_gravity else config.freeze_gravity

    @classmethod
    def set_gravity(cls, value):
        cls.gravity = value

    @classmethod
    def get_image(cls):
        if not cls.image:
            cls.image = utils.crop_image(utils.load_image(f'parts.png'), cls.sprite_rect)
        return cls.image

    @staticmethod
    def get_frame_speed(speed):
        return math.ceil(speed // config.fps)


class RotatingEntity(Entity):
    def __init__(self, *groups):
        super().__init__(*groups)
        self._angle = 0
        self._angle_delta = random.uniform(-2.0, 2.0)
        self.mask = pygame.mask.from_surface(self.image)

    def update(self, *args):
        super().update(*args)
        self.image = pygame.transform.rotate(self.get_image(), self.angle)
        self.rect = self.image.get_rect(center=self.rect.center)
        self.mask = pygame.mask.from_surface(self.image)
        self.angle = self.angle + self.angle_delta

    @property
    def angle(self):
        return self._angle

    @angle.setter
    def angle(self, value):
        self._angle = value

    @property
    def angle_delta(self):
        return self._angle_delta

    @angle_delta.setter
    def angle_delta(self, value):
        self._angle_delta = value
