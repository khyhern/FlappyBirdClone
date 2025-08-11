import pygame
import sys
import random

pygame.init()
WINDOW_WIDTH, WINDOW_HEIGHT = 800, 400
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
clock = pygame.time.Clock()

class Crow(pygame.sprite.Sprite):
    def __init__(self, pos, scale_factor=1):
        super().__init__()

        # Load frames
        self.frames = [
            pygame.image.load("crow_idle.png").convert_alpha(),
            pygame.image.load("crow_fly.png").convert_alpha()
        ]
        # Scale frames
        self.frames = [pygame.transform.scale_by(frame, scale_factor) for frame in self.frames]

        self.frame_index = 0
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect(midleft=pos)

        # Animation speed control
        self.animation_speed = 10  # frames per second
        self.timer = 0

        # Random movement speed
        self.speed = random.randint(-850, -600)

        # Trail for blur effect
        self.trail = []

    def animate(self, dt):
        self.timer += self.animation_speed * dt
        if self.timer >= 1:
            self.timer = 0
            self.frame_index = (self.frame_index + 1) % len(self.frames)
            self.image = self.frames[self.frame_index]

    def update(self, dt):
        self.animate(dt)

        # Record position for trail
        self.trail.append(self.rect.copy())
        if len(self.trail) > 6:
            self.trail.pop(0)

        # Move crow
        self.rect.x += self.speed * dt

        # Kill if off-screen
        if self.rect.right < 0:
            self.kill()

    def draw(self, surface):
        # Draw faded trail
        for i, old_rect in enumerate(self.trail):
            temp_img = self.image.copy()
            temp_img.set_alpha(100 - i * 15)  # transparency decreases
            surface.blit(temp_img, old_rect)
        # Draw main sprite
        surface.blit(self.image, self.rect)


# Group
all_sprites = pygame.sprite.Group()
crows = []

# Spawn first crow
crows.append(Crow((WINDOW_WIDTH, random.randint(50, 350)), scale_factor=0.5))
all_sprites.add(crows[-1])

last_spawn = pygame.time.get_ticks()

# Main loop
running = True
while running:
    dt = clock.tick(60) / 1000

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Spawn crow every 2 seconds
    if pygame.time.get_ticks() - last_spawn > 2000:
        crows.append(Crow((WINDOW_WIDTH, random.randint(50, 350)), scale_factor=0.5))
        all_sprites.add(crows[-1])
        last_spawn = pygame.time.get_ticks()

    # Update
    all_sprites.update(dt)

    # Draw
    screen.fill((30, 30, 30))
    for sprite in all_sprites:
        sprite.draw(screen)
    pygame.display.flip()

pygame.quit()
sys.exit()
