import sys
import os
import re
import pygame
import config

screen = 0


def init() -> pygame.Surface:
    if not pygame.get_init():
        pygame.init()
        pygame.mixer.init()
    global screen
    if not screen:
        screen = pygame.display.set_mode((config.width, config.height), pygame.FULLSCREEN)
    return screen


def terminate() -> None:
    pygame.quit()
    sys.exit()


def load_image(name: str, convert: bool = True) -> pygame.Surface:
    init()  # Fix uninitialized display
    image = pygame.image.load(os.path.join('media/images', name))
    return image.convert_alpha() if convert else image


def crop_image(image: pygame.Surface, rect: pygame.Rect) -> pygame.Surface:
    cropped = pygame.Surface(rect.size).convert()
    cropped.blit(image, (0, 0), rect)
    cropped.set_colorkey((0, 0, 0))
    return cropped


first_cap_re = re.compile('(.)([A-Z][a-z]+)')
all_cap_re = re.compile('([a-z0-9])([A-Z])')


def to_snake_case(string: str) -> str:
    s = first_cap_re.sub(r'\1_\2', string)
    return all_cap_re.sub(r'\1_\2', s).lower()
