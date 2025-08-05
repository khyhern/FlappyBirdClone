import pygame
import sys
import time
from random import randint
from settings import WINDOW_WIDTH, WINDOW_HEIGHT, FRAMERATE
from sprites import BG, Ground, Plane, Obstacle
from button import Button
from main import main_menu  # Make sure this doesn’t cause circular import issues


class Game:
    def __init__(self):
        pygame.init()
        self.display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Level 3")
        self.clock = pygame.time.Clock()
        self.active = True

        # Sprite groups
        self.all_sprites = pygame.sprite.Group()
        self.collision_sprites = pygame.sprite.Group()

        # Background setup
        bg_height = pygame.image.load("../graphics/environment/background.png").get_height()
        self.scale_factor = WINDOW_HEIGHT / bg_height
        BG(self.all_sprites, scale_factor=self.scale_factor)
        Ground(self.all_sprites, self.collision_sprites, scale_factor=self.scale_factor)
        self.plane = Plane(self.all_sprites, scale_factor=self.scale_factor / 1.7)

        # Obstacles
        self.obstacle_timer = pygame.USEREVENT + 1
        pygame.time.set_timer(self.obstacle_timer, 1400)

        # Score
        self.font = pygame.font.Font("../graphics/font/BD_Cartoon_Shout.ttf", 30)
        self.score = 0
        self.start_offset = 0

        # UI Menu
        self.menu_surf = pygame.image.load("../graphics/ui/menu.png").convert_alpha()
        self.menu_rect = self.menu_surf.get_rect(center=(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2))

        # Main Menu Button
        self.main_menu_button = Button(
            None,
            (WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2 + 160),
            "MAIN MENU",
            self.font,
            "white",
            "red"
        )

        # Music
        self.music = pygame.mixer.Sound("../sounds/music.wav")
        self.music.play(loops=-1)

        # Effects
        self.flash_surface = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.flash_surface.fill((255, 0, 0))
        self.flash_surface.set_alpha(0)
        self.flash_duration = 0.2
        self.flash_time = 0
        self.shake_duration = 0.3
        self.shake_time = 0
        self.shake_magnitude = 10

        # Gravity Flip
        self.distance_traveled = 0
        self.gravity_flipped = False
        self.gravity_interval_min = 2000
        self.gravity_interval_max = 3500
        self.gravity_warning_distance = 800
        self.next_gravity_flip_distance = randint(self.gravity_interval_min, self.gravity_interval_max)
        self.gravity_warning_active = False
        self.gravity_icon_visible = True
        self.gravity_icon_flash_interval = 0.3
        self.last_flash_time = 0

        icon_raw = pygame.image.load("../graphics/level_3/gravity.png").convert_alpha()
        icon_raw = pygame.transform.flip(icon_raw, False, True)
        self.gravity_icon = pygame.transform.scale(icon_raw, (80, 80))
        self.gravity_icon_rect = self.gravity_icon.get_rect(center=(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 4))

    def trigger_screen_effects(self):
        self.flash_time = time.time()
        self.shake_time = time.time()

    def apply_effects(self):
        now = time.time()
        if now - self.shake_time < self.shake_duration:
            offset_x = int((self.shake_magnitude * 2) * (0.5 - now % 0.1))
            offset_y = int((self.shake_magnitude * 2) * (0.5 - now % 0.1))
            self.display_surface.scroll(offset_x, offset_y)

        if now - self.flash_time < self.flash_duration:
            self.flash_surface.set_alpha(150)
            self.display_surface.blit(self.flash_surface, (0, 0))

    def check_gravity_zone(self):
        if self.distance_traveled >= self.next_gravity_flip_distance:
            self.gravity_flipped = not self.gravity_flipped
            self.plane.flip_gravity(self.gravity_flipped)

            self.gravity_warning_active = False
            self.gravity_icon_visible = True
            self.last_flash_time = time.time()

            self.next_gravity_flip_distance = self.distance_traveled + randint(
                self.gravity_interval_min, self.gravity_interval_max
            )

        elif self.distance_traveled >= self.next_gravity_flip_distance - self.gravity_warning_distance:
            self.gravity_warning_active = True
        else:
            self.gravity_warning_active = False

    def collisions(self):
        collided = pygame.sprite.spritecollide(
            self.plane, self.collision_sprites, False, pygame.sprite.collide_mask
        )
        if collided or self.plane.rect.top <= 0:
            for sprite in self.collision_sprites:
                if getattr(sprite, 'sprite_type', '') == 'obstacle':
                    sprite.kill()

            self.active = False
            self.plane.kill()
            self.trigger_screen_effects()

    def display_score(self):
        y = WINDOW_HEIGHT / 10 if self.active else WINDOW_HEIGHT / 2 + self.menu_rect.height / 1.5
        self.score = (pygame.time.get_ticks() - self.start_offset) // 1000 if self.active else self.score
        score_surf = self.font.render(str(self.score), True, "black")
        score_rect = score_surf.get_rect(midtop=(WINDOW_WIDTH / 2, y))
        self.display_surface.blit(score_surf, score_rect)

    def reset_game(self):
        self.plane = Plane(self.all_sprites, scale_factor=self.scale_factor / 1.7)
        self.active = True
        self.start_offset = pygame.time.get_ticks()
        self.gravity_flipped = False
        self.gravity_warning_active = False
        self.gravity_icon_visible = True
        self.distance_traveled = 0
        self.next_gravity_flip_distance = randint(
            self.gravity_interval_min, self.gravity_interval_max
        )

    def run(self):
        last_time = time.time()

        while True:
            dt = time.time() - last_time
            last_time = time.time()

            mouse_pos = pygame.mouse.get_pos()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if self.active:
                        self.plane.jump()
                    else:
                        if self.main_menu_button.check_for_input(mouse_pos):
                            main_menu()
                        else:
                            self.reset_game()

                elif event.type == self.obstacle_timer and self.active:
                    Obstacle(self.all_sprites, self.collision_sprites, scale_factor=self.scale_factor * 1.1)

            self.display_surface.fill("black")
            self.all_sprites.update(dt)
            self.all_sprites.draw(self.display_surface)

            if self.active:
                self.distance_traveled += 400 * dt
                self.check_gravity_zone()
                self.collisions()

                # Gravity warning UI
                if self.gravity_warning_active:
                    now = time.time()
                    if now - self.last_flash_time >= self.gravity_icon_flash_interval:
                        self.gravity_icon_visible = not self.gravity_icon_visible
                        self.last_flash_time = now
                    if self.gravity_icon_visible:
                        self.display_surface.blit(self.gravity_icon, self.gravity_icon_rect)
                elif self.gravity_flipped:
                    self.display_surface.blit(self.gravity_icon, self.gravity_icon_rect)
            else:
                # Death menu
                self.display_surface.blit(self.menu_surf, self.menu_rect)
                self.main_menu_button.change_color(mouse_pos)
                self.main_menu_button.update(self.display_surface)

            self.display_score()
            self.apply_effects()
            pygame.display.update()
            self.clock.tick(FRAMERATE)
