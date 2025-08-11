import pygame
import sys
import time
import settings
from settings import WINDOW_WIDTH, WINDOW_HEIGHT, FRAMERATE
from sprites import BG, Ground, Plane, Obstacle
from button import Button

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

        # Obstacles
        self.obstacle_timer = pygame.USEREVENT + 1
        pygame.time.set_timer(self.obstacle_timer, 1400)

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
                    Obstacle(self.all_sprites, self.collision_sprites, self.obstacles, scale_factor=self.scale_factor * 1.1)

            # Draw
            self.display_surface.fill("black")
            self.all_sprites.update(dt)
            self.all_sprites.draw(self.display_surface)

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
