import pygame
from settings import WINDOW_HEIGHT, WINDOW_WIDTH
from random import choice, randint

# --- Constants ---
BG_SCROLL_SPEED = 300
GROUND_SCROLL_SPEED = 360
OBSTACLE_SCROLL_SPEED = 400
JUMP_FORCE = -400
GRAVITY = 600
PLANE_ANIM_SPEED = 10

PLANE_IMG_PATH = '../graphics/plane/red{}.png'
BG_IMG_PATH = '../graphics/environment/background.png'
GROUND_IMG_PATH = '../graphics/environment/ground.png'
OBSTACLE_IMG_PATH = '../graphics/obstacles/{}.png'
JUMP_SOUND_PATH = '../sounds/jump.wav'

class BG(pygame.sprite.Sprite):
    def __init__(self, *groups, scale_factor):
        super().__init__(*groups)
        self.sprite_type = 'background'

        bg_image = pygame.image.load(BG_IMG_PATH).convert()
        full_height = int(bg_image.get_height() * scale_factor)
        full_width = int(bg_image.get_width() * scale_factor)
        full_sized_image = pygame.transform.scale(bg_image, (full_width, full_height))

        self.image = pygame.Surface((full_width * 2, full_height)).convert()
        self.image.blit(full_sized_image, (0, 0))
        self.image.blit(full_sized_image, (full_width, 0))

        self.rect = self.image.get_rect(topleft=(0, 0))
        self.pos = pygame.math.Vector2(self.rect.topleft)

    def update(self, dt):
        self.pos.x -= BG_SCROLL_SPEED * dt
        if self.rect.centerx <= 0:
            self.pos.x = 0
        self.rect.x = int(self.pos.x)


class Ground(pygame.sprite.Sprite):
    def __init__(self, *groups, scale_factor):
        super().__init__(*groups)
        self.sprite_type = 'ground'

        ground_surf = pygame.image.load(GROUND_IMG_PATH).convert_alpha()
        self.image = pygame.transform.scale(
            ground_surf,
            pygame.math.Vector2(ground_surf.get_size()) * scale_factor
        )

        self.rect = self.image.get_rect(bottomleft=(0, WINDOW_HEIGHT))
        self.pos = pygame.math.Vector2(self.rect.topleft)
        self.mask = pygame.mask.from_surface(self.image)

    def update(self, dt):
        self.pos.x -= GROUND_SCROLL_SPEED * dt
        if self.rect.centerx <= 0:
            self.pos.x = 0
        self.rect.x = int(self.pos.x)


class Plane(pygame.sprite.Sprite):
    def __init__(self, *groups, scale_factor):
        super().__init__(*groups)
        self.sprite_type = 'player'

        self.frames = []
        self.import_frames(scale_factor)
        self.frame_index = 0
        self.image = self.frames[self.frame_index]

        self.rect = self.image.get_rect(midleft=(WINDOW_WIDTH / 20, WINDOW_HEIGHT / 2))
        self.pos = pygame.math.Vector2(self.rect.topleft)
        self.gravity = GRAVITY
        self.direction = 0
        self.mask = pygame.mask.from_surface(self.image)

        self.jump_sound = pygame.mixer.Sound(JUMP_SOUND_PATH)
        self.jump_sound.set_volume(0.3)

    def import_frames(self, scale_factor):
        for i in range(3):
            surf = pygame.image.load(PLANE_IMG_PATH.format(i)).convert_alpha()
            scaled_surf = pygame.transform.scale(
                surf,
                pygame.math.Vector2(surf.get_size()) * scale_factor
            )
            self.frames.append(scaled_surf)

    def apply_gravity(self, dt):
        self.direction += self.gravity * dt
        self.pos.y += self.direction * dt
        self.rect.y = int(self.pos.y)

    def jump(self):
        self.jump_sound.play()
        self.direction = JUMP_FORCE

    def animate(self, dt):
        self.frame_index += PLANE_ANIM_SPEED * dt
        if self.frame_index >= len(self.frames):
            self.frame_index = 0
        self.image = self.frames[int(self.frame_index)]

    def rotate(self):
        rotated = pygame.transform.rotozoom(self.image, -self.direction * 0.06, 1)
        self.image = rotated
        self.mask = pygame.mask.from_surface(self.image)

    def update(self, dt):
        self.apply_gravity(dt)
        self.animate(dt)
        self.rotate()


class Obstacle(pygame.sprite.Sprite):
    def __init__(self, *groups, scale_factor):
        super().__init__(*groups)
        self.sprite_type = 'obstacle'

        orientation = choice(('up', 'down'))
        sprite_index = choice((0, 1))
        surf = pygame.image.load(OBSTACLE_IMG_PATH.format(sprite_index)).convert_alpha()

        self.image = pygame.transform.scale(
            surf,
            pygame.math.Vector2(surf.get_size()) * scale_factor
        )

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
        self.pos.x -= OBSTACLE_SCROLL_SPEED * dt
        self.rect.x = int(self.pos.x)
        if self.rect.right <= -100:
            self.kill()
