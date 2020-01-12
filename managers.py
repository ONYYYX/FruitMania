import typing
import screens
import game


class ScreensManager:
    next_screen: typing.Type[screens.Screen] = screens.Loading
    screen_dictionary = {}

    @classmethod
    def get_next_screen(cls) -> screens.Screen:
        return cls.screen_dictionary[cls.next_screen]

    @classmethod
    def set_next_screen(cls, screen: typing.Type[screens.Screen]) -> None:
        cls.next_screen = screen
        cls.screen_dictionary[cls.next_screen].reload()

    @classmethod
    def set_screens(cls, *screen_sequence: typing.Type[screens.Screen]):
        for screen in screen_sequence:
            cls.screen_dictionary[screen] = screen()


class GameManager:
    game_instance: game.Game = game.Game()

    @classmethod
    def get_instance(cls):
        return cls.game_instance
