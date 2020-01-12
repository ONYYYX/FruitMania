import pygame
import utils
import managers
import screens


def main():
    screen = utils.init()
    clock = pygame.time.Clock()
    managers.ScreensManager.set_screens(
        screens.Loading,
        screens.MainMenu,
        screens.Game,
        screens.EndTable
    )
    pygame.display.set_caption('Fruit Mania')
    while True:
        managers.ScreensManager.get_next_screen().loop(screen, clock)


if __name__ == '__main__':
    main()
