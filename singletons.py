import sys
import pygame
import fruits
import config


class _Group(pygame.sprite.Group):
    def empty(self):
        for sprite in self.sprites():
            sprite.kill()
        super().empty()


class _FruitsGroup(_Group):
    def delete_invisible(self) -> int:
        number = 0
        for fruit in self.sprites():
            # Верхнюю границу пересекать может, т.к. под силой тяжести все равно упадет
            if not (-fruit.rect.w < fruit.rect.x < config.width) or fruit.rect.y > config.height:
                x, y = fruit.velocity
                if y > 0:
                    if not isinstance(fruit, fruits.Bomb):
                        number += 1
                    fruit.kill()
        return number

    def delete(self):
        for fruit in self.sprites():
            fruit.kill()


class _PartsGroup(_Group):
    def delete_invisible(self):
        for part in self.sprites():
            # Верхнюю границу пересекать может, т.к. под силой тяжести все равно упадет
            if not (-part.rect.w < part.rect.x < config.width) or part.rect.y > config.height:
                x, y = part.velocity
                if y > 0:
                    part.kill()

    def delete(self):
        for part in self.sprites():
            part.kill()


class _BladesGroup(_Group):
    def start_session(self):
        for blade in self.sprites():
            blade.session_started = True

    def end_session(self):
        for blade in self.sprites():
            blade.session_started = False

    def add_mouse_track_pos(self):
        for blade in self.sprites():
            blade.add_mouse_track_pos(pygame.mouse.get_pos())

    # Specially for MainMenu (for getting screen which is connected to our fruit)
    def check_fruit_screen(self):
        for blade in self.sprites():
            if blade.session_started:
                fruit = pygame.sprite.spritecollideany(blade, FruitsGroup.get())
                if fruit:
                    if hasattr(fruit, 'screen'):
                        return getattr(fruit, 'screen')

    def check_fruit_cut(self):
        has_fruit, has_bomb = False, False
        for blade in self.sprites():
            if blade.session_started:
                fruit = pygame.sprite.spritecollideany(blade, FruitsGroup.get(), pygame.sprite.collide_mask)
                if fruit:
                    blade.add_cut_fruit(fruit)
                    if isinstance(fruit, fruits.Bomb):
                        has_bomb = True
                    has_fruit = True
        return has_fruit, has_bomb


class _ScoresGroup(_Group):
    pass


class _LivesGroup(_Group):
    pass


class _SplashesGroup(_Group):
    pass


class Group:
    group: pygame.sprite.Group = 0

    @classmethod
    def get(cls):
        if not cls.group:
            cls.group = getattr(sys.modules[cls.__module__], f'_{cls.__name__}')()
        return cls.group


class FruitsGroup(Group):
    pass


class PartsGroup(Group):
    pass


class BladesGroup(Group):
    pass


class ScoresGroup(Group):
    pass


class LivesGroup(Group):
    pass


class SplashesGroup(Group):
    pass
