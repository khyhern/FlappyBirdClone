import pygame
from settings import *
from random import choice, randint

class BG(pygame.sprite.Sprite):
    def __init__(self, groups, scale_factor):
        super().__init__(groups)

        # Load all background frames
        self.frames = [
            pygame.transform.scale(
                pygame.image.load(f'../graphics/environment/background{i}.png').convert(),
                (pygame.image.load(f'../graphics/environment/background{i}.png').get_width() * scale_factor,
                 pygame.image.load(f'../graphics/environment/background{i}.png').get_height() * scale_factor)
            )
            for i in range(20)  # Assuming 5 images: background0.png ... background4.png
        ]
        self.frame_index = 0
        self.image = pygame.Surface((self.frames[0].get_width() * 2, self.frames[0].get_height()))

        # Draw two copies for scrolling
        self.image.blit(self.frames[self.frame_index], (0, 0))
        self.image.blit(self.frames[self.frame_index], (self.frames[0].get_width(), 0))

        self.rect = self.image.get_rect(topleft=(0, 0))
        self.pos = pygame.math.Vector2(self.rect.topleft)

        self.animation_speed = 2  # frames per second

    def animate(self, dt):
        self.frame_index += self.animation_speed * dt
        if self.frame_index >= len(self.frames):
            self.frame_index = 0

        # Update image for new frame
        frame = self.frames[int(self.frame_index)]
        self.image = pygame.Surface((frame.get_width() * 2, frame.get_height()))
        self.image.blit(frame, (0, 0))
        self.image.blit(frame, (frame.get_width(), 0))

    def update(self, dt):
        # Animate
        self.animate(dt)

        # Scroll background left
        self.pos.x -= 300 * dt
        if self.rect.centerx <= 0:
            self.pos.x = 0
        self.rect.x = round(self.pos.x)

class Ground(pygame.sprite.Sprite):
    def __init__(self, groups, scale_factor):
        super().__init__(groups)
        self.sprite_type = 'ground'

        # Load and scale ground image
        ground_surf = pygame.image.load('../graphics/environment/ground1.png').convert_alpha()
        size = pygame.math.Vector2(ground_surf.get_size()) * scale_factor
        self.image = pygame.transform.scale(ground_surf, size)

        self.rect = self.image.get_rect(bottomleft=(0, WINDOW_HEIGHT))
        self.pos = pygame.math.Vector2(self.rect.topleft)

        self.mask = pygame.mask.from_surface(self.image)

    def update(self, dt):
        # Scroll ground left, loop seamlessly
        self.pos.x -= 360 * dt
        if self.rect.centerx <= 0:
            self.pos.x = 0
        self.rect.x = round(self.pos.x)

class Pony(pygame.sprite.Sprite):
    def __init__(self, groups, scale_factor):
        super().__init__(groups)

        # Load animation frames scaled by scale_factor
        self.import_frames(scale_factor)
        self.frame_index = 0
        self.image = self.frames[self.frame_index]

        self.rect = self.image.get_rect(midleft=(WINDOW_WIDTH / 20, WINDOW_HEIGHT / 2))
        self.pos = pygame.math.Vector2(self.rect.topleft)

        self.gravity = 600
        self.direction = 0

        self.mask = pygame.mask.from_surface(self.image)

        # Load jump sound and set volume
        self.jump_sound = pygame.mixer.Sound('../sounds/jump.wav')
        self.jump_sound.set_volume(0.3)

    def import_frames(self, scale_factor):
        # Load 3 frames of pony animation scaled appropriately
        self.frames = [
            pygame.transform.scale(
                pygame.image.load(f'../graphics/pony/fly{i}.png').convert_alpha(),
                pygame.math.Vector2(pygame.image.load(f'../graphics/pony/fly{i}.png').get_size()) * scale_factor
            ) for i in range(3)
        ]

    def apply_gravity(self, dt):
        # Apply gravity to vertical velocity and update position
        self.direction += self.gravity * dt
        self.pos.y += self.direction * dt
        self.rect.y = round(self.pos.y)

    def jump(self):
        # Play jump sound and set upward velocity
        self.jump_sound.play()
        self.direction = -400

    def animate(self, dt):
        # Animate pony frames cycling
        self.frame_index += 10 * dt
        if self.frame_index >= len(self.frames):
            self.frame_index = 0
        self.image = self.frames[int(self.frame_index)]

    def rotate(self):
        # Rotate pony sprite based on vertical speed
        rotated = pygame.transform.rotozoom(self.image, -self.direction * 0.06, 1)
        self.image = rotated
        self.mask = pygame.mask.from_surface(self.image)

    def update(self, dt):
        self.apply_gravity(dt)
        self.animate(dt)
        self.rotate()

class Obstacle(pygame.sprite.Sprite):
    def __init__(self, groups, scale_factor):
        super().__init__(groups)
        self.sprite_type = 'obstacle'

        # Randomly choose orientation and image
        orientation = choice(('up', 'down'))
        surf = pygame.image.load(f'../graphics/obstacles/{choice((3, 4))}.png').convert_alpha()
        self.image = pygame.transform.scale(surf, pygame.math.Vector2(surf.get_size()) * scale_factor)

        x = WINDOW_WIDTH + randint(40, 100)
        if orientation == 'up':
            y = WINDOW_HEIGHT + randint(10, 50)
            self.rect = self.image.get_rect(midbottom=(x, y))
        else:
            y = randint(-50, -10)
            self.image = pygame.transform.flip(self.image, False, True)
            self.rect = self.image.get_rect(midtop=(x, y))

        self.pos = pygame.math.Vector2(self.rect.topleft)
        self.mask = pygame.mask.from_surface(self.image)

    def update(self, dt):
        # Move obstacle left, destroy when offscreen
        self.pos.x -= 400 * dt
        self.rect.x = round(self.pos.x)
        if self.rect.right <= -100:
            self.kill()
