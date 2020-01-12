import random
import pygame
import utils
import config
import managers
import singletons


class AlphaAnimatedSprite(pygame.sprite.Sprite):
    def __init__(self, *groups):
        super().__init__(*groups)
        self.image: pygame.Surface = pygame.Surface((0, 0))
        self.alpha = 255

    def update(self, *args):
        if self.alpha <= 0:
            self.kill()
        self.alpha -= 2
        self.image.set_alpha(self.alpha)


class Life(pygame.sprite.Sprite):
    life_sprites = utils.load_image('screens/game/lives.png')
    image_blue = utils.crop_image(life_sprites, pygame.Rect(6, 2, 88, 84))
    image_red = utils.crop_image(life_sprites, pygame.Rect(6, 90, 88, 84))

    def __init__(self, pos, scale, *groups):
        super().__init__(singletons.LivesGroup.get(), *groups)
        self.scale = scale
        self.image = pygame.transform.scale(Life.image_blue, (
            int(Life.image_blue.get_rect().w * scale),
            int(Life.image_blue.get_rect().h * scale))
        )
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = pos

    def set_red(self):
        self.image = pygame.transform.scale(Life.image_red, (
            int(Life.image_blue.get_rect().w * self.scale),
            int(Life.image_blue.get_rect().h * self.scale))
        )


class FruitScore(AlphaAnimatedSprite):
    def __init__(self, text, score, pos, size=30, *groups):
        super().__init__(singletons.ScoresGroup.get(), *groups)
        self.font_size = size
        self.text = text
        self.score = score
        self.image = self.get_image()
        self.rect = self.image.get_rect(center=pos)

    def get_image(self):
        managers.GameManager.get_instance().score += self.score
        font = pygame.font.Font(config.game_font, self.font_size)
        if self.score >= 0:
            text = f'{self.text}: {abs(self.score)} points'
        else:
            text = f'{self.text}: -{abs(self.score)} points'
        return font.render(text, 0, (200, 100, 10))


class MouseFruitScore(FruitScore):
    def __init__(self, text, score, size=30, *groups):
        super().__init__(text, score, pygame.mouse.get_pos(), size, *groups)


class CenteredFruitScore(FruitScore):
    timer = 0
    positions = [
        (config.width // 2, config.height // 2),
        (config.width // 2 - config.width // 5, config.height // 2 - config.height // 5),
        (config.width // 2 - config.width // 5, config.height // 2 + config.height // 5),
        (config.width // 2 + config.width // 5, config.height // 2 - config.height // 5),
        (config.width // 2 + config.width // 5, config.height // 2 + config.height // 5),
    ]

    def __init__(self, text, score, size=50, *groups):
        super().__init__(text, score, self.positions[CenteredFruitScore.timer], size, *groups)
        CenteredFruitScore.timer = (CenteredFruitScore.timer + 1) % len(CenteredFruitScore.positions)


class Splash(AlphaAnimatedSprite):
    image = utils.load_image('screens/game/splashes.png', False)
    cropped_images = [
        utils.crop_image(image, pygame.Rect(15, 13, 169, 180)),
        utils.crop_image(image, pygame.Rect(205, 10, 185, 188)),
        utils.crop_image(image, pygame.Rect(10, 207, 196, 180)),
        utils.crop_image(image, pygame.Rect(202, 208, 195, 183)),
        utils.crop_image(image, pygame.Rect(397, 7, 198, 189)),
        utils.crop_image(image, pygame.Rect(598, 11, 202, 189)),
        utils.crop_image(image, pygame.Rect(387, 211, 224, 182)),
        utils.crop_image(image, pygame.Rect(610, 205, 185, 191))
    ]

    def __init__(self, pos, *groups):
        super().__init__(singletons.SplashesGroup.get(), *groups)
        self.image = random.choice(self.cropped_images)
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = pos
