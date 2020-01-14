import sys
import random
import pygame
import singletons
import screens
import objects
import sprites
import utils
import config


class Fruit(objects.RotatingEntity):
    def __init__(self, throw_sound=True, *groups):
        super().__init__(singletons.FruitsGroup.get(), *groups)
        self.part_class = self.__class__.__name__ + 'Part'
        self._score = 5
        self.sound_throw = pygame.mixer.Sound(config.sounds['fruit_throw'])
        self.sound_cut = pygame.mixer.Sound(config.sounds['fruit_cut'])
        if throw_sound:
            self.sound_throw.play()

    def cut(self):
        x, y = self.rect.x, self.rect.y
        x_vel, y_vel = self.velocity
        part_class = getattr(sys.modules[self.__module__], self.part_class)
        part_class((x, y), singletons.PartsGroup().get()).velocity = (
            x_vel - random.randrange(200),
            y_vel - random.randrange(-50, 50)
        )
        part_class((x, y), singletons.PartsGroup().get()).velocity = (
            x_vel + random.randrange(200),
            y_vel - random.randrange(-50, 50)
        )
        sprites.MouseFruitScore('Fruit', self.score)
        sprites.Splash((x, y))
        self.sound_cut.play()
        self.kill()

    @property
    def score(self):
        return self._score

    @classmethod
    def get_image(cls):
        if not cls.image:
            cls.image = utils.crop_image(utils.load_image(config.images['fruits']), cls.sprite_rect)
        return cls.image


class Bomb(Fruit):
    sprite_rect = pygame.Rect(0, 0, 142, 170)

    def __init__(self, throw_sound=True, *groups):
        super().__init__(throw_sound, *groups)
        self._score = -10
        self.sound_throw = pygame.mixer.Sound(config.sounds['bomb_throw'])
        self.sound_cut = pygame.mixer.Sound(config.sounds['bomb_explode'])
        self.sound_use = pygame.mixer.Sound(config.sounds['bomb_use'])
        if throw_sound:
            self.sound_use.set_volume(0.1)
            self.sound_use.play()
            self.sound_throw.play()

    def cut(self):
        sprites.FruitScore('Bomb', self.score, pygame.mouse.get_pos())
        self.sound_cut.play()
        self.kill()

    def kill(self):
        self.sound_use.stop()
        super().kill()


class RedApple(Fruit):
    sprite_rect = pygame.Rect(200, 34, 112, 112)


class GreenApple(Fruit):
    sprite_rect = pygame.Rect(373, 28, 105, 113)


class Banana(Fruit):
    sprite_rect = pygame.Rect(540, 10, 111, 152)


class Coconut(Fruit):
    sprite_rect = pygame.Rect(696, 10, 140, 150)


class Watermelon(Fruit):
    sprite_rect = pygame.Rect(860, 3, 150, 164)


class Kiwi(Fruit):
    sprite_rect = pygame.Rect(21, 192, 138, 130)


class Lemon(Fruit):
    sprite_rect = pygame.Rect(211, 203, 89, 105)


class Lime(Fruit):
    sprite_rect = pygame.Rect(365, 195, 118, 118)


class Mango(Fruit):
    sprite_rect = pygame.Rect(522, 189, 144, 131)


class Orange(Fruit):
    sprite_rect = pygame.Rect(704, 196, 121, 123)


class Pear(Fruit):
    sprite_rect = pygame.Rect(850, 183, 148, 148)


class Pineapple(Fruit):
    sprite_rect = pygame.Rect(5, 334, 154, 176)


class Starfruit(Fruit):
    sprite_rect = pygame.Rect(194, 358, 128, 133)


class Strawberry(Fruit):
    sprite_rect = pygame.Rect(370, 363, 108, 125)


class Garnet(Fruit):
    sprite_rect = pygame.Rect(508, 353, 173, 150)


class FrozenApple(Fruit):
    sprite_rect = pygame.Rect(680, 353, 172, 145)

    def __init__(self, throw_sound=True, *groups):
        super().__init__(throw_sound, *groups)
        self.sound_impact = pygame.mixer.Sound(config.sounds['fruit_impact'])

    def cut(self):
        self.sound_impact.play()
        pygame.time.set_timer(screens.Arcade.event_start_freeze, 1)
        pygame.time.set_timer(screens.Arcade.event_remove_freeze, 5000)
        super().cut()


class Part(objects.RotatingEntity):
    base_image: pygame.Surface = 0
    sprite_rect = []

    def __init__(self, pos, *groups):
        self.original_image = 0
        super().__init__(singletons.PartsGroup.get(), *groups)
        self.move(pos)

    def get_image(self):
        if not self.original_image:
            self.original_image = utils.crop_image(self.get_base_image(), random.choice(self.sprite_rect))
        return self.original_image

    @classmethod
    def get_base_image(cls):
        if not cls.base_image:
            cls.base_image = utils.load_image(config.images['parts'])
        return cls.base_image


class RedApplePart(Part):
    sprite_rect = [
        pygame.Rect(540, 40, 114, 86),
        pygame.Rect(712, 40, 110, 87),
        pygame.Rect(884, 34, 96, 103),
    ]


class GreenApplePart(Part):
    sprite_rect = [
        pygame.Rect(26, 207, 116, 95),
        pygame.Rect(198, 208, 125, 99),
        pygame.Rect(365, 194, 123, 121),
    ]


class BananaPart(Part):
    sprite_rect = [
        pygame.Rect(547, 201, 100, 110),
        pygame.Rect(719, 201, 102, 108),
        pygame.Rect(893, 203, 77, 99),
    ]


class CoconutPart(Part):
    sprite_rect = [
        pygame.Rect(17, 366, 141, 114),
        pygame.Rect(185, 371, 147, 106),
        pygame.Rect(354, 372, 139, 110),
    ]


class WatermelonPart(Part):
    sprite_rect = [
        pygame.Rect(522, 355, 144, 141),
        pygame.Rect(693, 358, 149, 126),
        pygame.Rect(862, 362, 144, 133),
    ]


class KiwiPart(Part):
    sprite_rect = [
        pygame.Rect(21, 538, 133, 118),
        pygame.Rect(190, 533, 143, 118),
        pygame.Rect(356, 541, 136, 115),
    ]


class LemonPart(Part):
    sprite_rect = [
        pygame.Rect(529, 540, 129, 110),
        pygame.Rect(704, 545, 114, 97),
        pygame.Rect(872, 535, 123, 117),
    ]


class LimePart(Part):
    sprite_rect = [
        pygame.Rect(23, 714, 117, 105),
        pygame.Rect(188, 712, 133, 109),
        pygame.Rect(350, 709, 143, 109),
    ]


class MangoPart(Part):
    sprite_rect = [
        pygame.Rect(531, 710, 125, 105),
        pygame.Rect(712, 720, 116, 105),
        pygame.Rect(864, 715, 135, 110),
    ]


class OrangePart(Part):
    sprite_rect = [
        pygame.Rect(20, 872, 126, 118),
        pygame.Rect(184, 883, 143, 106),
        pygame.Rect(349, 876, 150, 120),
    ]


class PearPart(Part):
    sprite_rect = [
        pygame.Rect(525, 859, 139, 153),
        pygame.Rect(692, 879, 136, 110),
        pygame.Rect(853, 864, 157, 125),
    ]


class PineapplePart(Part):
    sprite_rect = [
        pygame.Rect(23, 1031, 128, 158),
        pygame.Rect(187, 1060, 128, 104),
        pygame.Rect(362, 1058, 120, 100),
    ]


class StarfruitPart(Part):
    sprite_rect = [
        pygame.Rect(520, 1051, 139, 125),
        pygame.Rect(695, 1038, 140, 131),
        pygame.Rect(866, 1048, 146, 128),
    ]


class StrawberryPart(Part):
    sprite_rect = [
        pygame.Rect(33, 1207, 105, 138),
        pygame.Rect(200, 1203, 105, 142),
        pygame.Rect(374, 1203, 103, 142),
    ]


class GarnetPart(Part):
    sprite_rect = [
        pygame.Rect(505, 1210, 174, 143),
        pygame.Rect(684, 1212, 149, 139),
        pygame.Rect(851, 1210, 164, 146),
    ]


class FrozenApplePart(Part):
    sprite_rect = [
        pygame.Rect(18, 1379, 131, 125)
    ]
