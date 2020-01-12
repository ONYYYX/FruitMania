import sys
import os
import re
import pygame
import config


def init() -> pygame.Surface:
    if not pygame.get_init():
        pygame.init()
        pygame.mixer.init()
    return pygame.display.set_mode((config.width, config.height))


def terminate() -> None:
    pygame.quit()
    sys.exit()


def load_image(name, convert=True) -> pygame.Surface:
    init()  # Fix uninitialized display
    image = pygame.image.load(os.path.join('media', name))
    return image.convert_alpha() if convert else image


def crop_image(image: pygame.Surface, rect: pygame.Rect) -> pygame.Surface:
    cropped: pygame.Surface = pygame.Surface(rect.size).convert()
    cropped.set_colorkey((0, 0, 0))
    cropped.blit(image, (0, 0), rect)
    return cropped


first_cap_re = re.compile('(.)([A-Z][a-z]+)')
all_cap_re = re.compile('([a-z0-9])([A-Z])')


def to_snake_case(string):
    s = first_cap_re.sub(r'\1_\2', string)
    return all_cap_re.sub(r'\1_\2', s).lower()
