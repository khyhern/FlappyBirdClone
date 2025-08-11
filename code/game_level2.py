import pygame
import sys
import time
import random
import settings
from settings import WINDOW_WIDTH, WINDOW_HEIGHT, FRAMERATE
from sprites import BG, Ground, Plane, Obstacle
from button import Button


class Crow(pygame.sprite.Sprite):
    def __init__(self, all_sprites, obstacle_sprites, pos, scale_factor=1):
        super().__init__(all_sprites, obstacle_sprites)

        # Load frames
        self.frames = [
            pygame.image.load("../graphics/level_2/crow_idle.png").convert_alpha(),
            pygame.image.load("../graphics/level_2/crow_fly.png").convert_alpha()
        ]

        # Scale frames smaller
        shrink_factor = 0.5  # 50% size
        self.frames = [
            pygame.transform.scale_by(frame, scale_factor * shrink_factor)
            for frame in self.frames
        ]

        self.frame_index = 0
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect(midleft=pos)
        self.mask = pygame.mask.from_surface(self.image)

        # Animation
        self.animation_speed = 10  # frames per second
        self.timer = 0

        # Movement speed (leftward)
        self.speed = random.randint(-850, -600)  # pixels/sec

        # Store old positions for ghost trail effect
        self.trail = []

        # Label
        self.font = pygame.font.Font("../graphics/font/BD_Cartoon_Shout.ttf", 20)
        self.label_surface = self.font.render("Crow", True, "white")

    def animate(self, dt):
        self.timer += self.animation_speed * dt
        if self.timer >= 1:
            self.timer = 0
            self.frame_index = (self.frame_index + 1) % len(self.frames)
            self.image = self.frames[self.frame_index]
            self.mask = pygame.mask.from_surface(self.image)

    def update(self, dt):
        self.animate(dt)

        # Add current position to trail
        self.trail.append(self.rect.copy())
        if len(self.trail) > 10:  # keep only last 5 positions
            self.trail.pop(0)

        # Move crow
        self.rect.x += self.speed * dt

        # Remove if off-screen
        if self.rect.right < 0:
            self.kill()

    def draw(self, surface):
        max_alpha = 180  # Start of trail visibility
        min_alpha = 0  # End of trail visibility
        fade_range = max_alpha - min_alpha

        # Draw old positions first (faded)
        for i, old_rect in enumerate(self.trail):
            temp_img = self.image.copy()
            fade = max_alpha - ((len(self.trail) - i - 1) * (fade_range // len(self.trail)))     #alpha for trail effects
            temp_img.set_alpha(fade)
            surface.blit(temp_img, old_rect)

        # Draw current crow
        surface.blit(self.image, self.rect)


class Game:
    def __init__(self):
        pygame.init()
        self.display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Level 2")
        self.clock = pygame.time.Clock()
        self.active = True

        # Sprite groups
        self.all_sprites = pygame.sprite.Group()
        self.collision_sprites = pygame.sprite.Group()  # ground + obstacles
        self.obstacles = pygame.sprite.Group()  # just obstacles

        # Background
        bg_height = pygame.image.load("../graphics/environment/background.png").get_height()
        self.scale_factor = WINDOW_HEIGHT / bg_height
        BG(self.all_sprites, scale_factor=self.scale_factor)
        Ground(self.all_sprites, self.collision_sprites, scale_factor=self.scale_factor)
        self.plane = Plane(self.all_sprites, scale_factor=self.scale_factor / 1.7)

        # Timers
        self.obstacle_timer = pygame.USEREVENT + 1
        pygame.time.set_timer(self.obstacle_timer, 1400)

        self.crow_timer = pygame.USEREVENT + 2
        pygame.time.set_timer(self.crow_timer, 3000)  # every 3 seconds

        # Score
        self.font = pygame.font.Font("../graphics/font/BD_Cartoon_Shout.ttf", 30)
        self.score = 0
        self.start_offset = pygame.time.get_ticks()

        # Death menu
        self.menu_surf = pygame.image.load("../graphics/ui/menu.png").convert_alpha()
        self.menu_rect = self.menu_surf.get_rect(center=(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2))

        # Main menu button (clickable on death screen)
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
        self.music.set_volume(settings.BGM_VOLUME)
        self.music.play(loops=-1)

    def collisions(self):
        if pygame.sprite.spritecollide(self.plane, self.obstacles, False, pygame.sprite.collide_mask) \
                or self.plane.rect.top <= 0 \
                or self.plane.rect.bottom >= WINDOW_HEIGHT:
            for sprite in self.obstacles:
                sprite.kill()
            self.active = False
            self.plane.kill()

    def display_score(self):
        if self.active:
            self.score = (pygame.time.get_ticks() - self.start_offset) // 1000
            y = WINDOW_HEIGHT / 10
        else:
            y = WINDOW_HEIGHT / 2 + (self.menu_rect.height / 1.5)

        score_surf = self.font.render(str(self.score), True, "black")
        score_rect = score_surf.get_rect(midtop=(WINDOW_WIDTH / 2, y))
        self.display_surface.blit(score_surf, score_rect)

    def reset_game(self):
        self.all_sprites.empty()
        self.collision_sprites.empty()
        self.obstacles.empty()

        BG(self.all_sprites, scale_factor=self.scale_factor)
        Ground(self.all_sprites, self.collision_sprites, scale_factor=self.scale_factor)
        self.plane = Plane(self.all_sprites, scale_factor=self.scale_factor / 1.7)

        self.active = True
        self.start_offset = pygame.time.get_ticks()
        self.score = 0

    def run(self):
        last_time = time.time()

        while True:
            self.music.set_volume(settings.BGM_VOLUME)
            dt = time.time() - last_time
            last_time = time.time()
            mouse_pos = pygame.mouse.get_pos()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if self.active:
                        self.plane.jump()
                    else:
                        if self.main_menu_button.check_for_input(mouse_pos):
                            self.music.stop()
                            from main import main_menu  # import here to avoid circular import
                            main_menu()
                        else:
                            self.reset_game()

                elif event.type == self.obstacle_timer and self.active:
                    Obstacle(self.all_sprites, self.collision_sprites, self.obstacles,
                             scale_factor=self.scale_factor * 1.1)


                elif event.type == self.crow_timer and self.active:
                    if random.random() < 0.2:  # 20% chance for 2 crows
                        min_distance = 180
                        y1 = random.randint(WINDOW_HEIGHT // 5, WINDOW_HEIGHT * 2 // 3)

                        while True:
                            y2 = random.randint(WINDOW_HEIGHT // 5, WINDOW_HEIGHT * 2 // 3)
                            if abs(y2 - y1) >= min_distance:
                                break
                        Crow(self.all_sprites, self.obstacles, pos=(WINDOW_WIDTH, y1), scale_factor=self.scale_factor / 1.5)
                        Crow(self.all_sprites, self.obstacles, pos=(WINDOW_WIDTH, y2), scale_factor=self.scale_factor / 1.5)

                    else:  # 80% chance for 1 crow
                        y = random.randint(WINDOW_HEIGHT // 5, WINDOW_HEIGHT * 2 // 3)
                        Crow(self.all_sprites, self.obstacles, pos=(WINDOW_WIDTH, y), scale_factor=self.scale_factor / 1.5)

            # Draw
            self.display_surface.fill("black")
            self.all_sprites.update(dt)
            for sprite in self.all_sprites:
                if hasattr(sprite, "draw"):
                    sprite.draw(self.display_surface)
                else:
                    self.display_surface.blit(sprite.image, sprite.rect)

            if self.active:
                self.collisions()
            else:
                self.display_surface.blit(self.menu_surf, self.menu_rect)
                self.main_menu_button.change_color(mouse_pos)
                self.main_menu_button.update(self.display_surface)

            self.display_score()
            pygame.display.update()
            self.clock.tick(FRAMERATE)


if __name__ == "__main__":
    Game().run()
