import typing
import screens
import game
import database


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

    @classmethod
    def get_screen(cls, screen: typing.Type[screens.Screen]) -> screens.Screen:
        return cls.screen_dictionary[screen]


class GameManager:
    game_instance: game.Game = game.Game()

    @classmethod
    def get_instance(cls):
        return cls.game_instance


class DatabaseManager:
    db_instance: database.Database = database.Database()

    @classmethod
    def get_instance(cls):
        return cls.db_instance
