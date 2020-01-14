import typing
import datetime
import random
import pygame
import managers
import singletons
import fruits
import blades
import sprites
import utils
import config


class Screen:
    image: pygame.Surface = 0

    def __init__(self):
        self.image = self.get_image()
        self.rect = self.image.get_rect()

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
            if event.type == pygame.QUIT or event.type == pygame.KEYDOWN and pygame.key.get_pressed()[pygame.K_ESCAPE]:
                managers.DatabaseManager.get_instance().close()
                utils.terminate()
            self.handle_event(event)

    def handle_event(self, event: pygame.event.Event) -> None:
        pass  # For inheritance

    def update_screen(self, screen: pygame.Surface) -> None:
        screen.fill((0, 0, 0))
        screen.blit(self.image, self.rect)

    def loop_post(self, elapsed: float) -> None:
        pass  # For inheritance

    @classmethod
    def get_image(cls) -> pygame.Surface:
        if not cls.image:
            screen_name = utils.to_snake_case(cls.__name__)
            cls.image = pygame.transform.scale(
                utils.load_image(f'screens/{screen_name}/{screen_name}.png'),
                (config.width, config.height)
            )
        return cls.image


class Loading(Screen):
    def __init__(self):
        super().__init__()
        self.elapsed = 0.0

    def loop_pre(self, screen: pygame.Surface):
        if self.elapsed >= 2.0:
            self.elapsed = 0.0
            managers.ScreensManager.set_next_screen(MainMenu)

    def loop_post(self, elapsed: float) -> None:
        self.elapsed += elapsed


class MainMenu(Screen):
    event_change_screen = pygame.USEREVENT + 1
    music = pygame.mixer.Sound(config.sounds['music'])

    logo_part_size = (config.width // 5, config.height // 10)
    logo_images = {
        'fruit': pygame.transform.scale(utils.load_image(config.images['fruit_label']), logo_part_size),
        'mania': pygame.transform.scale(utils.load_image(config.images['mania_label']), logo_part_size),
    }
    logo_pos = {
        'fruit': (config.width // 2 - logo_images['fruit'].get_rect().w, config.height // 10),
        'mania': (config.width // 2 + 10, config.height // 10)
    }

    ninja_image = utils.load_image(config.images['ninja'])
    ninja_pos = (
        config.width // 2 - ninja_image.get_rect().w // 2 + 50,
        config.height // 2 - ninja_image.get_rect().h // 2
    )

    circles_images = {
        'classic': utils.crop_image(utils.load_image(config.images['circles'], False), pygame.Rect(1125, 0, 231, 227)),
        'arcade': utils.crop_image(utils.load_image(config.images['circles'], False), pygame.Rect(16, 242, 200, 200)),
        'quit': utils.crop_image(utils.load_image(config.images['circles'], False), pygame.Rect(692, 20, 190, 190)),
        'shop': utils.crop_image(utils.load_image(config.images['circles'], False), pygame.Rect(1142, 237, 205, 205))
    }
    circles_pos = {
        'classic': circles_images['classic'].get_rect(x=(config.width // 5), y=(config.height // 4)),
        'arcade': circles_images['arcade'].get_rect(x=(config.width - config.width // 5), y=(config.height // 3)),
        'quit': circles_images['quit'].get_rect(x=(config.width // 3), y=(config.height // 2)),
        'shop': circles_images['shop'].get_rect(x=(config.width // 2), y=(config.height // 1.5))
    }

    fruits_pos = {
        'classic': (circles_pos['classic'].x + 56, circles_pos['classic'].y + 56),
        'arcade': (circles_pos['arcade'].x + 45, circles_pos['arcade'].y + 45),
        'quit': (circles_pos['quit'].x + 43, circles_pos['quit'].y + 43),
        'shop': (circles_pos['shop'].x + 40, circles_pos['shop'].y + 40)
    }

    def __init__(self):
        super().__init__()
        self.circles_images_editable = {
            'classic': self.circles_images['classic'],
            'arcade': self.circles_images['arcade'],
            'quit': self.circles_images['quit'],
            'shop': self.circles_images['shop']
        }
        self.angle = 0
        self.angle_delta = 0.5 * 1.0 if random.random() else -1.0
        self.next_screen = 0
        self.active = False

    def reload(self) -> None:
        self.active = True
        self.music.play()
        blades.Blade()

        classic_sprite = fruits.RedApple(False)
        classic_sprite.personal_gravity = 0
        classic_sprite.move(self.fruits_pos['classic'])
        classic_sprite.screen = Classic

        arcade_sprite = fruits.Banana(False)
        arcade_sprite.personal_gravity = 0
        arcade_sprite.move(self.fruits_pos['arcade'])
        arcade_sprite.screen = Arcade

        quit_sprite = fruits.Lemon(False)
        quit_sprite.personal_gravity = 0
        quit_sprite.move(self.fruits_pos['quit'])
        quit_sprite.screen = Quit

        shop_sprite = fruits.Starfruit(False)
        shop_sprite.personal_gravity = 0
        shop_sprite.move(self.fruits_pos['shop'])
        shop_sprite.screen = Classic

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == MainMenu.event_change_screen:
            self.delete_all()
            managers.ScreensManager.set_next_screen(self.next_screen)
        if not self.active:
            return
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                singletons.BladesGroup.get().start_session()
        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                singletons.BladesGroup.get().end_session()
        if event.type == pygame.MOUSEMOTION:
            singletons.BladesGroup.get().add_mouse_track_pos()
            self.next_screen = singletons.BladesGroup.get().check_fruit_screen()
            has_fruit, temp = singletons.BladesGroup.get().check_fruit_cut()
            if has_fruit:
                self.active = False
                pygame.time.set_timer(MainMenu.event_change_screen, 1500)

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
            self.circles_images_editable[k] = pygame.transform.rotate(
                self.circles_images[k],
                self.angle
            ).convert_alpha()
            self.circles_pos[k] = self.circles_images_editable[k].get_rect(center=self.circles_pos[k].center)
        self.angle = self.angle + self.angle_delta

    def draw_circles(self, screen: pygame.Surface) -> None:
        for k, v in self.circles_images_editable.items():
            screen.blit(self.circles_images_editable[k], self.circles_pos[k])

    def delete_all(self) -> None:
        self.music.stop()
        pygame.time.set_timer(MainMenu.event_change_screen, 0)
        singletons.FruitsGroup.get().empty()
        singletons.PartsGroup.get().empty()
        singletons.BladesGroup.get().empty()
        singletons.ScoresGroup.get().empty()
        singletons.SplashesGroup.get().empty()


class Classic(Screen):
    mode = 1
    event_change_screen = pygame.USEREVENT + 2
    event_drop_fruit = pygame.USEREVENT + 3
    event_drop_bomb = pygame.USEREVENT + 4

    sound_game_start = pygame.mixer.Sound(config.sounds['game_start'])
    sound_lose_life = pygame.mixer.Sound(config.sounds['lose_life'])

    fruits_classes = [
        'RedApple',
        'GreenApple',
        'Banana',
        'Coconut',
        'Watermelon',
        'Kiwi',
        'Lemon',
        'Lime',
        'Mango',
        'Orange',
        'Pear',
        'Pineapple',
        'Strawberry'
    ]

    def __init__(self):
        super().__init__()
        self.active = True
        self.blindness = 0
        self.elapsed_blade_session = 0.0
        self.elapsed_critical = 0.0
        self.lives = []

    def reload(self) -> None:
        managers.GameManager.get_instance().reload(Classic.mode)
        pygame.time.set_timer(Classic.event_drop_fruit, int(random.uniform(0.5, 2.0) * 1000))
        pygame.time.set_timer(Classic.event_drop_bomb, int(random.uniform(10.0, 15.0) * 1000))
        self.sound_game_start.play()
        self.active = True
        self.blindness = 0
        self.elapsed_blade_session = 0.0
        self.elapsed_critical = 0.0
        self.lives = self.create_lives()
        blades.Blade()

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == Classic.event_change_screen:
            self.delete_all()
            managers.DatabaseManager.get_instance().add_score(managers.GameManager.get_instance().score, Classic.mode)
            pygame.time.set_timer(Classic.event_change_screen, 0)
            managers.ScreensManager.set_next_screen(EndTable)
        if not self.active:
            return
        if event.type == Classic.event_drop_fruit:
            pygame.time.set_timer(Classic.event_drop_fruit, int(random.uniform(0.5, 2.0) * 1000))
            for _ in range(random.randrange(4)):
                self.create_fruit(random.choice(Classic.fruits_classes))
        if event.type == Classic.event_drop_bomb:
            pygame.time.set_timer(Classic.event_drop_bomb, int(random.uniform(5.0, 7.0) * 1000))
            for _ in range(random.randrange(2)):
                self.create_fruit('Bomb')
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                singletons.BladesGroup.get().start_session()
        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                singletons.BladesGroup.get().end_session()
        if event.type == pygame.MOUSEMOTION:
            singletons.BladesGroup.get().add_mouse_track_pos()
            has_fruit, has_bomb = singletons.BladesGroup.get().check_fruit_cut()
            if has_fruit and not has_bomb:
                managers.GameManager.get_instance().critical_combo += 1
                self.elapsed_critical = 0.0
            if has_bomb:
                self.explode_bomb()

    def update_screen(self, screen: pygame.Surface) -> None:
        super().update_screen(screen)
        self.lose_life(singletons.FruitsGroup.get().delete_invisible())
        singletons.SplashesGroup.get().update()
        singletons.SplashesGroup.get().draw(screen)
        singletons.PartsGroup.get().update()
        singletons.PartsGroup.get().delete_invisible()
        singletons.PartsGroup.get().draw(screen)
        singletons.FruitsGroup.get().update()
        singletons.FruitsGroup.get().draw(screen)
        singletons.BladesGroup.get().update(screen)
        singletons.LivesGroup.get().draw(screen)
        singletons.ScoresGroup.get().update()
        singletons.ScoresGroup.get().draw(screen)
        self.draw_blindness(screen)
        self.draw_score(screen)
        self.draw_best_score(screen)

    def loop_post(self, elapsed: float) -> None:
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
                pygame.mixer.Sound(config.sounds['critical']).play()
            self.elapsed_critical = 0.0
            managers.GameManager.get_instance().critical_combo = 0

    def draw_blindness(self, screen: pygame.Surface):
        if self.blindness:
            surface = pygame.Surface((config.width, config.height))
            surface = surface.convert_alpha(surface)
            surface.fill((255, 255, 255, self.blindness))
            screen.blit(surface, (0, 0))
            self.blindness -= 2

    def draw_score(self, screen: pygame.Surface) -> None:
        font = pygame.font.Font(config.game_font, 30)
        text = font.render(f'Score: {managers.GameManager.get_instance().score}', 1, (200, 100, 10))
        screen.blit(text, (20, 20))

    def draw_best_score(self, screen: pygame.Surface) -> None:
        font = pygame.font.Font(config.game_font, 30)
        text = font.render(f'Best: {managers.GameManager.get_instance().best_score}', 1, (200, 100, 10))
        screen.blit(text, (20, 60))

    def create_lives(self) -> typing.List[sprites.Life]:
        return [
            sprites.Life((config.width - sprites.Life.image_blue.get_rect().w - 20, 20), 0.6),
            sprites.Life((config.width - sprites.Life.image_blue.get_rect().w - 40, 80), 0.8),
            sprites.Life((config.width - sprites.Life.image_blue.get_rect().w - 60, 160), 1.0)
        ]

    def lose_life(self, number: int) -> None:
        while number and self.active:
            if managers.GameManager.get_instance().fruits_missed < 3:
                self.sound_lose_life.play()
                self.lives[managers.GameManager.get_instance().fruits_missed].set_red()
                managers.GameManager.get_instance().fruits_missed += 1
            if managers.GameManager.get_instance().fruits_missed >= 3:
                self.active = False
                pygame.time.set_timer(Classic.event_change_screen, 1500)
            number -= 1

    def create_fruit(self, fruit_class: str) -> None:
        if self.active:
            fruit = getattr(fruits, fruit_class)()
            x, y = random.randrange(config.width), config.height + 50
            fruit.move((x, y))
            x_vel = random.randint(100, 400) * (-1 if fruit.rect.x > config.width // 2 else 1)
            y_vel = random.randint(-1000, -500)
            fruit.velocity = (x_vel, y_vel)

    def explode_bomb(self) -> None:
        self.delete_all()
        self.blindness = 240
        managers.GameManager.get_instance().critical_combo = 0
        pygame.time.set_timer(Classic.event_change_screen, 1000)

    def delete_all(self) -> None:
        pygame.time.set_timer(Classic.event_drop_fruit, 0)
        pygame.time.set_timer(Classic.event_drop_bomb, 0)
        singletons.FruitsGroup.get().empty()
        singletons.PartsGroup.get().empty()
        singletons.BladesGroup.get().empty()
        singletons.ScoresGroup.get().empty()
        singletons.LivesGroup.get().empty()
        singletons.SplashesGroup.get().empty()


class Arcade(Screen):
    mode = 2
    event_change_screen = pygame.USEREVENT + 1
    event_drop_fruit = pygame.USEREVENT + 2
    event_drop_bomb = pygame.USEREVENT + 3
    event_drop_sweet = pygame.USEREVENT + 4
    event_start_freeze = pygame.USEREVENT + 5
    event_remove_freeze = pygame.USEREVENT + 6

    sound_game_start = pygame.mixer.Sound(config.sounds['game_start'])
    sound_lose_life = pygame.mixer.Sound(config.sounds['lose_life'])

    fruits_classes = [
        'RedApple',
        'GreenApple',
        'Banana',
        'Coconut',
        'Watermelon',
        'Kiwi',
        'Lemon',
        'Lime',
        'Mango',
        'Orange',
        'Pear',
        'Pineapple',
        'Strawberry'
    ]

    def __init__(self):
        super().__init__()
        self.active = True
        self.freeze = False
        self.blindness = 0
        self.time = datetime.time()
        self.seconds = 0
        self.elapsed_blade_session = 0.0
        self.elapsed_critical = 0.0
        self.freeze_screen, self.freeze_text, self.freeze_pos = self.create_freeze()

    def reload(self) -> None:
        managers.GameManager.get_instance().reload(Arcade.mode)
        pygame.time.set_timer(Arcade.event_drop_fruit, int(random.uniform(0.5, 2.0) * 1000))
        pygame.time.set_timer(Arcade.event_drop_bomb, int(random.uniform(10.0, 15.0) * 1000))
        pygame.time.set_timer(Arcade.event_drop_sweet, int(random.uniform(10.0, 15.0) * 1000))
        self.sound_game_start.play()
        self.active = True
        self.freeze = False
        self.blindness = 0
        self.time = datetime.datetime.now() + datetime.timedelta(seconds=config.arcade_time)
        self.seconds = 0
        self.elapsed_blade_session = 0.0
        self.elapsed_critical = 0.0
        blades.Blade()

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == Arcade.event_change_screen:
            self.delete_all()
            managers.DatabaseManager.get_instance().add_score(managers.GameManager.get_instance().score, Arcade.mode)
            pygame.time.set_timer(Arcade.event_change_screen, 0)
            managers.ScreensManager.set_next_screen(EndTable)
        if not self.active:
            return
        if event.type == Arcade.event_drop_fruit:
            pygame.time.set_timer(Arcade.event_drop_fruit, int(random.uniform(0.5, 2.0) * 1000))
            for _ in range(random.randrange(4)):
                self.create_fruit(random.choice(Arcade.fruits_classes))
        if event.type == Arcade.event_drop_bomb:
            pygame.time.set_timer(Arcade.event_drop_bomb, int(random.uniform(3.0, 7.0) * 1000))
            for _ in range(random.randrange(3)):
                self.create_fruit('Bomb')
        if event.type == Arcade.event_drop_sweet:
            pygame.time.set_timer(Arcade.event_drop_sweet, int(random.uniform(10.0, 15.0) * 1000))
            self.create_fruit('FrozenApple')
        if event.type == Arcade.event_start_freeze:
            pygame.time.set_timer(Arcade.event_drop_sweet, 0)
            pygame.time.set_timer(Arcade.event_start_freeze, 0)
            self.freeze = True
        if event.type == Arcade.event_remove_freeze:
            pygame.time.set_timer(Arcade.event_drop_sweet, int(random.uniform(10.0, 15.0) * 1000))
            self.freeze = False
            pygame.time.set_timer(Arcade.event_remove_freeze, 0)
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                singletons.BladesGroup.get().start_session()
        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                singletons.BladesGroup.get().end_session()
        if event.type == pygame.MOUSEMOTION:
            singletons.BladesGroup.get().add_mouse_track_pos()
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
        singletons.ScoresGroup.get().update()
        singletons.ScoresGroup.get().draw(screen)
        self.draw_blindness(screen)
        self.draw_freeze(screen)
        self.draw_score(screen)
        self.draw_best_score(screen)
        self.draw_timer(screen)

    def loop_post(self, elapsed: float) -> None:
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
                pygame.mixer.Sound(config.sounds['critical']).play()
            self.elapsed_critical = 0.0
            managers.GameManager.get_instance().critical_combo = 0

    def draw_blindness(self, screen: pygame.Surface):
        if self.blindness:
            surface = pygame.Surface((config.width, config.height))
            surface = surface.convert_alpha(surface)
            surface.fill((255, 255, 255, self.blindness))
            screen.blit(surface, (0, 0))
            self.blindness -= 2

    def create_freeze(self):
        surface = pygame.Surface((config.width, config.height))
        surface = surface.convert_alpha(surface)
        surface.fill((10, 10, 150, 100))
        font = pygame.font.Font(config.game_font, 60)
        text = font.render('Effect: Freeze', 1, (10, 10, 200))
        pos = (config.width // 2 - text.get_rect().w // 2, config.height // 10)
        return surface, text, pos

    def draw_freeze(self, screen: pygame.Surface):
        if self.freeze:
            screen.blit(self.freeze_screen, (0, 0))
            screen.blit(self.freeze_text, self.freeze_pos)

    def draw_score(self, screen: pygame.Surface) -> None:
        font = pygame.font.Font(config.game_font, 30)
        text = font.render(f'Score: {managers.GameManager.get_instance().score}', 1, (200, 100, 10))
        screen.blit(text, (20, 20))

    def draw_best_score(self, screen: pygame.Surface) -> None:
        font = pygame.font.Font(config.game_font, 30)
        text = font.render(f'Best: {managers.GameManager.get_instance().best_score}', 1, (200, 100, 10))
        screen.blit(text, (20, 60))

    def draw_timer(self, screen: pygame.Surface) -> None:
        font = pygame.font.Font(config.game_font, 30)
        if self.active:
            self.seconds = (self.time - datetime.datetime.now()).total_seconds()
        minutes = int((self.seconds % 3600) / 60)
        seconds = int(self.seconds % 60)
        text = font.render(f'{minutes}:{str(seconds).rjust(2, "0")}', 1, (200, 100, 10))
        screen.blit(text, (200, 20))
        if not minutes and not seconds and self.active:
            self.active = False
            pygame.time.set_timer(Arcade.event_change_screen, 1500)

    def create_fruit(self, fruit_class: str) -> None:
        if self.active:
            fruit = getattr(fruits, fruit_class)()
            x, y = random.randrange(config.width), config.height + 50
            fruit.move((x, y))
            x_vel = random.randint(100, 400) * (-1 if fruit.rect.x > config.width // 2 else 1)
            y_vel = random.randint(-1000, -500)
            fruit.velocity = (x_vel, y_vel)

    def explode_bomb(self) -> None:
        self.clear_sprites()
        self.blindness = 240
        managers.GameManager.get_instance().critical_combo = 0
        pygame.time.set_timer(Arcade.event_drop_fruit, int(random.uniform(7.0, 8.0) * 1000))
        pygame.time.set_timer(Arcade.event_drop_bomb, int(random.uniform(7.0, 8.0) * 1000))
        pygame.time.set_timer(Arcade.event_drop_sweet, int(random.uniform(10.0, 15.0) * 1000))
        pygame.time.set_timer(Arcade.event_remove_freeze, 1)

    def clear_sprites(self):
        singletons.FruitsGroup.get().empty()
        singletons.PartsGroup.get().empty()

    def delete_all(self) -> None:
        pygame.time.set_timer(Arcade.event_drop_fruit, 0)
        pygame.time.set_timer(Arcade.event_drop_bomb, 0)
        pygame.time.set_timer(Arcade.event_drop_sweet, 0)
        pygame.time.set_timer(Arcade.event_remove_freeze, 1)
        singletons.FruitsGroup.get().empty()
        singletons.PartsGroup.get().empty()
        singletons.BladesGroup.get().empty()
        singletons.ScoresGroup.get().empty()
        singletons.SplashesGroup.get().empty()


class EndTable(Screen):
    event_change_screen = pygame.USEREVENT + 1
    table_image = utils.load_image(config.images['table'])
    font = pygame.font.Font(config.game_font, 30)
    sound_game_over = pygame.mixer.Sound(config.sounds['game_over'])

    def __init__(self):
        super().__init__()
        self.table_rect = pygame.Rect(0, 0, 0, 0)
        self.score_image = pygame.Surface((0, 0))
        self.best_score_image = pygame.Surface((0, 0))
        self.score_rect = pygame.Rect(0, 0, 0, 0)
        self.best_score_rect = pygame.Rect(0, 0, 0, 0)

    def reload(self) -> None:
        self.sound_game_over.play()
        self.table_rect = self.table_image.get_rect(center=(config.width // 2, config.height // 2))
        self.score_image = self.font.render(
            f'Total: {managers.GameManager.get_instance().score}', 1, (200, 100, 10)
        )
        self.best_score_image = self.font.render(
            f'Best score: {managers.GameManager.get_instance().best_score}', 1, (200, 100, 10)
        )
        self.score_rect = self.score_image.get_rect(center=self.table_rect.center)
        self.best_score_rect = self.best_score_image.get_rect(center=self.table_rect.center)
        self.score_rect.y -= (self.table_rect.h // 8 * 2)
        self.best_score_rect.y -= (self.table_rect.h // 8 * 1)

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == EndTable.event_change_screen:
            pygame.time.set_timer(EndTable.event_change_screen, 0)
            managers.ScreensManager.set_next_screen(MainMenu)
        if event.type == pygame.MOUSEBUTTONDOWN:
            pygame.time.set_timer(EndTable.event_change_screen, 1000)

    def update_screen(self, screen: pygame.Surface) -> None:
        super().update_screen(screen)
        self.draw_table(screen)
        self.draw_score(screen)

    def draw_table(self, screen: pygame.Surface) -> None:
        screen.blit(self.table_image, self.table_rect)

    def draw_score(self, screen: pygame.Surface) -> None:
        screen.blit(self.score_image, self.score_rect)
        screen.blit(self.best_score_image, self.best_score_rect)


class Quit(Screen):
    def reload(self):
        utils.terminate()

    @classmethod
    def get_image(cls) -> pygame.Surface:
        return pygame.Surface((0, 0))
