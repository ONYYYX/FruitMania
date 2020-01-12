import random
import pygame
import fruits
import blades
import utils
import config
import managers
import sprites
import singletons


class Screen:
    image: pygame.Surface = 0

    def __init__(self):
        self.image: pygame.Surface = self.get_image()
        self.rect: pygame.Rect = self.image.get_rect()

    def reload(self):
        pass  # For inheritance

    def loop(self, screen: pygame.Surface, clock: pygame.time.Clock) -> None:
        self.loop_pre(screen)
        self.handle_events()
        self.update_screen(screen)
        pygame.display.flip()
        elapsed = clock.tick(config.fps) / 1000.0
        self.loop_post(elapsed)

    def loop_pre(self, screen: pygame.Surface) -> None:
        pass  # For inheritance

    def handle_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                utils.terminate()
            self.handle_event(event)

    def handle_event(self, event: pygame.event.Event) -> None:
        pass  # For inheritance

    def update_screen(self, screen: pygame.Surface) -> None:
        screen.fill((0, 0, 0))
        screen.blit(self.image, self.rect)

    def loop_post(self, elapsed) -> None:
        pass  # For inheritance

    @classmethod
    def get_image(cls):
        if not cls.image:
            screen_name = utils.to_snake_case(cls.__name__)
            cls.image = utils.load_image(f'screens/{screen_name}/{screen_name}.png')
            cls.image = pygame.transform.scale(cls.image, (config.width, config.height))
        return cls.image


class Loading(Screen):
    def __init__(self):
        super().__init__()
        self.elapsed = 0.0

    def loop_pre(self, screen: pygame.Surface):
        if self.elapsed >= 2.0:
            self.elapsed = 0.0
            managers.ScreensManager.set_next_screen(MainMenu)

    def loop_post(self, elapsed) -> None:
        self.elapsed += elapsed


class MainMenu(Screen):
    event_change_screen = pygame.USEREVENT + 1
    music = pygame.mixer.Sound('media/music/nature_bgm.ogg')
    logo_part_size = (config.width // 5, config.height // 10)
    logo_images = {
        'fruit': pygame.transform.scale(utils.load_image('screens/main_menu/label_fruit.png'), logo_part_size),
        'mania': pygame.transform.scale(utils.load_image('screens/main_menu/label_mania.png'), logo_part_size),
    }
    logo_pos = {
        'fruit': (config.width // 2 - logo_images['fruit'].get_rect().w, config.height // 10),
        'mania': (config.width // 2 + 10, config.height // 10)
    }

    ninja_image = utils.load_image('screens/main_menu/ninja.png')
    ninja_pos = (
        config.width // 2 - ninja_image.get_rect().w // 2 + 50,
        config.height // 2 - ninja_image.get_rect().h // 2
    )

    circles_images = {
        'new_game': utils.crop_image(
            utils.load_image(f'screens/main_menu/circles.png', False),
            pygame.Rect(0, 0, 225, 225)
        )
    }
    circles_pos = {
        'new_game': circles_images['new_game'].get_rect(x=144, y=144)
    }

    fruits_pos = {
        'new_game': (200, 200)
    }

    def __init__(self):
        super().__init__()
        self.circles_images_editable = {
            'new_game': self.circles_images['new_game']
        }
        self.angle = 0
        self.angle_delta = 0.5 * 1.0 if random.random() else -1.0

    def reload(self):
        self.music.play()
        blades.Blade()
        new_game_sprite = fruits.RedApple(False)
        new_game_sprite.personal_gravity = 0
        new_game_sprite.move(self.fruits_pos['new_game'])
        new_game_sprite.screen = Game

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                singletons.BladesGroup.get().start_session()
        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                singletons.BladesGroup.get().end_session()
        if event.type == pygame.MOUSEMOTION:
            singletons.BladesGroup.get().add_mouse_track_pos(pygame.mouse.get_pos())
            has_fruit, temp = singletons.BladesGroup.get().check_fruit_cut()
            if has_fruit:
                pygame.time.set_timer(MainMenu.event_change_screen, 1500)
        if event.type == MainMenu.event_change_screen:
            self.delete_all()
            managers.ScreensManager.set_next_screen(Game)

    def update_screen(self, screen: pygame.Surface) -> None:
        super().update_screen(screen)
        self.draw_logo(screen)
        self.draw_ninja(screen)
        self.update_circles()
        self.draw_circles(screen)
        singletons.FruitsGroup.get().update()
        singletons.FruitsGroup.get().delete_invisible()
        singletons.FruitsGroup.get().draw(screen)
        singletons.PartsGroup.get().update()
        singletons.PartsGroup.get().delete_invisible()
        singletons.PartsGroup.get().draw(screen)
        singletons.BladesGroup.get().update(screen)

    def draw_logo(self, screen: pygame.Surface) -> None:
        screen.blit(self.logo_images['fruit'], self.logo_pos['fruit'])
        screen.blit(self.logo_images['mania'], self.logo_pos['mania'])

    def draw_ninja(self, screen: pygame.Surface) -> None:
        screen.blit(self.ninja_image, self.ninja_pos)

    def update_circles(self) -> None:
        for k, v in self.circles_images_editable.items():
            self.circles_images_editable[k] = pygame.transform.rotate(self.circles_images[k], self.angle).convert_alpha()
            self.circles_pos[k] = self.circles_images_editable[k].get_rect(center=self.circles_pos[k].center)
        self.angle = self.angle + self.angle_delta

    def draw_circles(self, screen: pygame.Surface) -> None:
        for k, v in self.circles_images_editable.items():
            screen.blit(self.circles_images_editable[k], self.circles_pos[k])

    def delete_all(self):
        self.music.stop()
        pygame.time.set_timer(MainMenu.event_change_screen, 0)
        singletons.FruitsGroup.get().empty()
        singletons.PartsGroup.get().empty()
        singletons.BladesGroup.get().empty()
        singletons.ScoresGroup.get().empty()
        singletons.SplashesGroup.get().empty()


class Game(Screen):
    event_change_screen = pygame.USEREVENT + 2
    event_drop_fruit = pygame.USEREVENT + 3
    event_drop_bomb = pygame.USEREVENT + 4
    sound_game_start = pygame.mixer.Sound('media/sounds/game-start.ogg')
    sound_lose_life = pygame.mixer.Sound('media/sounds/lose_life.ogg')
    fruits_classes = [
        'RedApple',
        'GreenApple',
        'Banana',
        'Coconut',
        'Watermelon',
        'Lemon',
        'Lime',
        'Orange',
        'Pineapple',
        'Strawberry'
    ]

    def __init__(self):
        super().__init__()
        self.blindness = 0
        self.elapsed_blade_session = 0.0
        self.elapsed_critical = 0.0
        self.lives = []

    def reload(self):
        managers.GameManager.get_instance().reload()
        self.sound_game_start.play()
        pygame.time.set_timer(Game.event_drop_fruit, int(random.uniform(0.5, 2.0) * 1000))
        pygame.time.set_timer(Game.event_drop_bomb, int(random.uniform(10.0, 15.0) * 1000))
        self.blindness = 0
        self.elapsed_blade_session = 0.0
        self.elapsed_critical = 0.0
        self.lives = self.create_lives()
        blades.Blade()

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == Game.event_drop_fruit:
            pygame.time.set_timer(Game.event_drop_fruit, int(random.uniform(0.5, 2.0) * 1000))
            for _ in range(random.randrange(4)):
                self.create_fruit(random.choice(Game.fruits_classes))
        if event.type == Game.event_drop_bomb:
            pygame.time.set_timer(Game.event_drop_bomb, int(random.uniform(5.0, 7.0) * 1000))
            for _ in range(random.randrange(2)):
                self.create_fruit('Bomb')
        if event.type == Game.event_change_screen:
            pygame.time.set_timer(Game.event_change_screen, 0)
            managers.ScreensManager.set_next_screen(EndTable)
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                singletons.BladesGroup.get().start_session()
        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                singletons.BladesGroup.get().end_session()
        if event.type == pygame.MOUSEMOTION:
            singletons.BladesGroup.get().add_mouse_track_pos(pygame.mouse.get_pos())
            has_fruit, has_bomb = singletons.BladesGroup.get().check_fruit_cut()
            if has_fruit and not has_bomb:
                managers.GameManager.get_instance().critical_combo += 1
                self.elapsed_critical = 0.0
            if has_bomb:
                self.explode_bomb()

    def update_screen(self, screen: pygame.Surface) -> None:
        super().update_screen(screen)
        singletons.SplashesGroup.get().update()
        singletons.SplashesGroup.get().draw(screen)
        singletons.PartsGroup.get().update()
        singletons.PartsGroup.get().delete_invisible()
        singletons.PartsGroup.get().draw(screen)
        singletons.FruitsGroup.get().update()
        singletons.FruitsGroup.get().delete_invisible()
        singletons.FruitsGroup.get().draw(screen)
        singletons.BladesGroup.get().update(screen)
        singletons.LivesGroup.get().draw(screen)
        singletons.ScoresGroup.get().update()
        singletons.ScoresGroup.get().draw(screen)
        self.draw_blindness(screen)
        self.draw_score(screen)

    def loop_post(self, elapsed) -> None:
        self.elapsed_blade_session += elapsed
        if self.elapsed_blade_session >= 1.0:
            self.elapsed_blade_session = 0.0
            singletons.BladesGroup.get().end_session()
            if pygame.mouse.get_pressed()[0]:
                singletons.BladesGroup.get().start_session()
        self.elapsed_critical += elapsed
        if self.elapsed_critical >= 1.0:
            if managers.GameManager.get_instance().critical_combo > 3:
                sprites.CenteredFruitScore('Critical', managers.GameManager.get_instance().critical_combo * 2)
                pygame.mixer.Sound('media/sounds/critical.ogg').play()
            self.elapsed_critical = 0.0
            managers.GameManager.get_instance().critical_combo = 0

    def draw_blindness(self, screen: pygame.Surface):
        if self.blindness:
            surface = pygame.Surface((config.width, config.height))
            surface = surface.convert_alpha(surface)
            surface.fill((255, 255, 255, self.blindness))
            screen.blit(surface, (0, 0))
            self.blindness -= 2

    def draw_score(self, screen: pygame.Surface):
        font = pygame.font.Font(config.game_font, 30)
        text = font.render(f'Score: {managers.GameManager.get_instance().score}', 1, (200, 100, 10))
        screen.blit(text, (20, 20))

    def create_lives(self):
        return [
            sprites.Life((config.width - sprites.Life.image_blue.get_rect().w - 20, 20), 0.6),
            sprites.Life((config.width - sprites.Life.image_blue.get_rect().w - 40, 80), 0.8),
            sprites.Life((config.width - sprites.Life.image_blue.get_rect().w - 60, 160), 1.0)
        ]

    def create_fruit(self, fruit_class):
        fruit = getattr(fruits, fruit_class)()
        x, y = random.randrange(config.width), config.height + 50
        fruit.move((x, y))
        x_vel = random.randint(100, 400) * (-1 if fruit.rect.x > config.width // 2 else 1)
        y_vel = random.randint(-1000, -500)
        fruit.velocity = (x_vel, y_vel)

    def explode_bomb(self):
        if managers.GameManager.get_instance().bombs_exploded < 3:
            self.sound_lose_life.play()
            self.lives[managers.GameManager.get_instance().bombs_exploded].set_red()
            managers.GameManager.get_instance().bombs_exploded += 1
            self.clear_sprites()
            self.blindness = 240
            managers.GameManager.get_instance().critical_combo = 0
            pygame.time.set_timer(Game.event_drop_fruit, int(random.uniform(3.0, 4.0) * 1000))
            pygame.time.set_timer(Game.event_drop_bomb, int(random.uniform(5.0, 10.0) * 1000))
        if managers.GameManager.get_instance().bombs_exploded >= 3:
            self.delete_all()
            pygame.time.set_timer(Game.event_change_screen, 2000)

    def clear_sprites(self):
        singletons.FruitsGroup.get().empty()
        singletons.PartsGroup.get().empty()

    def delete_all(self):
        pygame.time.set_timer(Game.event_drop_fruit, 0)
        pygame.time.set_timer(Game.event_drop_bomb, 0)
        singletons.FruitsGroup.get().empty()
        singletons.PartsGroup.get().empty()
        singletons.BladesGroup.get().empty()
        singletons.ScoresGroup.get().empty()
        singletons.LivesGroup.get().empty()
        singletons.SplashesGroup.get().empty()


class EndTable(Screen):
    table_image = utils.load_image('screens/end_table/table.png')
    font = pygame.font.Font(config.game_font, 30)
    sound_game_over = pygame.mixer.Sound('media/sounds/game-over.ogg')

    def __init__(self):
        super().__init__()
        self.table_rect = self.table_image.get_rect(center=(config.width // 2, config.height // 2))
        self.score_image = self.font.render(
            f'Total: {managers.GameManager.get_instance().score}', 1, (200, 100, 10)
        )
        self.score_rect = self.score_image.get_rect(center=self.table_rect.center)
        self.score_rect.y -= self.table_rect.h // 4

    def reload(self):
        self.sound_game_over.play()

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == Game.event_change_screen:
            pygame.time.set_timer(Game.event_change_screen, 0)
            managers.ScreensManager.set_next_screen(MainMenu)
        if event.type == pygame.MOUSEBUTTONDOWN:
            pygame.time.set_timer(Game.event_change_screen, 1000)

    def update_screen(self, screen: pygame.Surface) -> None:
        super().update_screen(screen)
        self.draw_table(screen)
        self.draw_score(screen)

    def draw_table(self, screen: pygame.Surface) -> None:
        screen.blit(self.table_image, self.table_rect)

    def draw_score(self, screen: pygame.Surface) -> None:
        screen.blit(self.score_image, self.score_rect)