import pygame
import managers
import screens
import utils
import config


def main() -> None:
    screen = utils.init()
    clock = pygame.time.Clock()
    managers.ScreensManager.set_screens(
        screens.Loading,
        screens.MainMenu,
        screens.Game,
        screens.EndTable,
        screens.Quit,
    )
    pygame.display.set_caption(config.game_name)
    while True:
        managers.ScreensManager.get_next_screen().loop(screen, clock)


if __name__ == '__main__':
    main()
