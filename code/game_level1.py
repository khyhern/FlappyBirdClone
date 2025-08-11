import pygame
import sys
import time
from settings import *
from code.spritesLevelOne import BG, Ground, Pony, Obstacle

class Game:
    def __init__(self):
        # Initialize pygame, display, and clock
        pygame.init()
        self.display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Level 1")
        self.clock = pygame.time.Clock()
        self.active = True

        # Sprite groups for drawing and collision detection
        self.all_sprites = pygame.sprite.Group()
        self.collision_sprites = pygame.sprite.Group()

        # Calculate scale factor for images based on background height
        bg_image = pygame.image.load('../graphics/environment/background0.png')
        self.scale_factor = WINDOW_HEIGHT / bg_image.get_height()

        # Create initial game objects
        BG(self.all_sprites, self.scale_factor)
        Ground([self.all_sprites, self.collision_sprites], self.scale_factor)
        self.pony = Pony(self.all_sprites, self.scale_factor / 1.7)

        # Setup obstacle spawn timer event
        self.obstacle_timer = pygame.USEREVENT + 1
        pygame.time.set_timer(self.obstacle_timer, 1400)

        # Font setup for score display
        self.font = pygame.font.Font('../graphics/font/BD_Cartoon_Shout.ttf', 30)
        self.score = 0
        self.start_offset = 0

        # Load menu image and set center position
        self.menu_surf = pygame.image.load('../graphics/ui/menu.png').convert_alpha()
        self.menu_rect = self.menu_surf.get_rect(center=(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2))

        # Background music setup and loop play
        self.music = pygame.mixer.Sound('../sounds/music1.wav')
        self.music.play(loops=-1)

    def collisions(self):
        # Check for collisions between pony and obstacles or ceiling
        collision = pygame.sprite.spritecollide(
            self.pony, self.collision_sprites, False, pygame.sprite.collide_mask
        ) or self.pony.rect.top <= 0

        if collision:
            # Remove all obstacle sprites on collision
            for sprite in self.collision_sprites.sprites():
                if getattr(sprite, 'sprite_type', None) == 'obstacle':
                    sprite.kill()
            self.active = False
            self.pony.kill()

    def display_score(self):
        # Display current score; position depends on game state
        y = WINDOW_HEIGHT / 10 if self.active else WINDOW_HEIGHT / 2 + self.menu_rect.height / 1.5
        if self.active:
            # Score is time elapsed since game start in seconds
            self.score = (pygame.time.get_ticks() - self.start_offset) // 1000

        score_surf = self.font.render(str(self.score), True, 'black')
        score_rect = score_surf.get_rect(midtop=(WINDOW_WIDTH / 2, y))
        self.display_surface.blit(score_surf, score_rect)

    def run(self):
        last_time = time.time()

        while True:
            # Calculate delta time for smooth movement
            dt = time.time() - last_time
            last_time = time.time()

            # Event handling loop
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.active:
                        self.pony.jump()
                    else:
                        # Reset game after crash
                        self.pony = Pony(self.all_sprites, self.scale_factor / 1.7)
                        self.active = True
                        self.start_offset = pygame.time.get_ticks()

                if event.type == self.obstacle_timer and self.active:
                    # Spawn new obstacles at timed intervals
                    Obstacle([self.all_sprites, self.collision_sprites], self.scale_factor * 1.1)

            # Draw background and sprites
            self.display_surface.fill('black')
            self.all_sprites.update(dt)
            self.all_sprites.draw(self.display_surface)
            self.display_score()

            # Check collisions if game active, else show menu
            if self.active:
                self.collisions()
            else:
                self.display_surface.blit(self.menu_surf, self.menu_rect)

            pygame.display.update()
            # Optional framerate cap
            # self.clock.tick(FRAMERATE)

if __name__ == '__main__':
    Game().run()
