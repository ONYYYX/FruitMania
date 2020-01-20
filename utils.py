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
        screen = pygame.display.set_mode((config.width, config.height))
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


def create_pause_info(pos: tuple) -> tuple:
    font = pygame.font.Font(config.game_font, 30)
    text = font.render('Pause - Escape', 1, (200, 100, 10))
    return text, pos


pause_board_image = load_image(config.images['pause_board'])


def create_pause_board() -> tuple:
    board_pos = pause_board_image.get_rect(center=(config.width // 2, config.height // 2))
    font = pygame.font.Font(config.game_font, 35)
    text1 = font.render('Do you want to exit?', 1, (100, 150, 10))
    pos1 = text1.get_rect(center=(board_pos.centerx, board_pos.centery - 30))
    text2 = font.render('Escape - No', 1, (100, 150, 10))
    pos2 = text1.get_rect(center=(board_pos.centerx, board_pos.centery))
    text3 = font.render('Left Alt - Yes', 1, (100, 150, 10))
    pos3 = text1.get_rect(center=(board_pos.centerx, board_pos.centery + 30))
    return board_pos, text1, pos1, text2, pos2, text3, pos3


def draw_pause_board(pause_data: list, surface: pygame.Surface) -> None:
    surface.blit(pause_board_image, pause_data[0])
    surface.blit(pause_data[1], pause_data[2])
    surface.blit(pause_data[3], pause_data[4])
    surface.blit(pause_data[5], pause_data[6])


def draw_pause_info(pause_info: list, surface: pygame.Surface) -> None:
    surface.blit(pause_info[0], pause_info[1])
