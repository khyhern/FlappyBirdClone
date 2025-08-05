import pygame
import sys
import time
from settings import WINDOW_WIDTH, WINDOW_HEIGHT, FRAMERATE
from sprites import BG, Ground, Plane, Obstacle


class Game:
    def __init__(self):
        # Initialize Pygame
        pygame.init()
        self.display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Flappy Bird - Level 3")
        self.clock = pygame.time.Clock()
        self.active = True

        # Sprite groups
        self.all_sprites = pygame.sprite.Group()
        self.collision_sprites = pygame.sprite.Group()

        # Calculate scale factor based on background image
        bg_height = pygame.image.load("../graphics/environment/background.png").get_height()
        self.scale_factor = WINDOW_HEIGHT / bg_height

        # Create game sprites
        BG(self.all_sprites, scale_factor=self.scale_factor)
        Ground(self.all_sprites, self.collision_sprites, scale_factor=self.scale_factor)
        self.plane = Plane(self.all_sprites, scale_factor=self.scale_factor / 1.7)

        # Obstacle spawn timer
        self.obstacle_timer = pygame.USEREVENT + 1
        pygame.time.set_timer(self.obstacle_timer, 1400)

        # Font and score
        self.font = pygame.font.Font("../graphics/font/BD_Cartoon_Shout.ttf", 30)
        self.score = 0
        self.start_offset = 0

        # Game over UI
        self.menu_surf = pygame.image.load("../graphics/ui/menu.png").convert_alpha()
        self.menu_rect = self.menu_surf.get_rect(center=(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2))

        # Background music
        self.music = pygame.mixer.Sound("../sounds/music.wav")
        self.music.play(loops=-1)

        # Flash + Shake Effect
        self.flash_surface = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.flash_surface.fill((255, 0, 0))
        self.flash_surface.set_alpha(0)

        self.flash_duration = 0.2
        self.flash_time = 0

        self.shake_duration = 0.3
        self.shake_time = 0
        self.shake_magnitude = 10

    def trigger_screen_effects(self):
        self.flash_time = time.time()
        self.shake_time = time.time()

    def apply_effects(self):
        # Screen Shake
        offset_x, offset_y = 0, 0
        if time.time() - self.shake_time < self.shake_duration:
            offset_x = int((self.shake_magnitude * 2) * (0.5 - time.time() % 0.1))
            offset_y = int((self.shake_magnitude * 2) * (0.5 - time.time() % 0.1))
            self.display_surface.scroll(offset_x, offset_y)

        # Flash
        if time.time() - self.flash_time < self.flash_duration:
            self.flash_surface.set_alpha(150)
            self.display_surface.blit(self.flash_surface, (0, 0))

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
        if self.active:
            self.score = (pygame.time.get_ticks() - self.start_offset) // 1000
            y = WINDOW_HEIGHT / 10
        else:
            y = WINDOW_HEIGHT / 2 + self.menu_rect.height / 1.5

        score_surf = self.font.render(str(self.score), True, "black")
        score_rect = score_surf.get_rect(midtop=(WINDOW_WIDTH / 2, y))
        self.display_surface.blit(score_surf, score_rect)

    def run(self):
        last_time = time.time()

        while True:
            # Delta time
            dt = time.time() - last_time
            last_time = time.time()

            # Event handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if self.active:
                        self.plane.jump()
                    else:
                        # Restart game
                        self.plane = Plane(self.all_sprites, scale_factor=self.scale_factor / 1.7)
                        self.active = True
                        self.start_offset = pygame.time.get_ticks()

                elif event.type == self.obstacle_timer and self.active:
                    Obstacle(self.all_sprites, self.collision_sprites, scale_factor=self.scale_factor * 1.1)

            # Game logic
            self.display_surface.fill("black")
            self.all_sprites.update(dt)
            self.all_sprites.draw(self.display_surface)
            self.display_score()

            # Check collisions or show menu
            if self.active:
                self.collisions()
            else:
                self.display_surface.blit(self.menu_surf, self.menu_rect)

            # Apply screen effects
            self.apply_effects()

            # Final screen update
            pygame.display.update()
            self.clock.tick(FRAMERATE)
