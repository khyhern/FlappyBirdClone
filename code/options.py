# options.py
import pygame
import sys
import settings
from button import Button

pygame.init()

class Slider:
    def __init__(self, x, y, w, h, start_val):
        self.rect = pygame.Rect(x, y, w, h)
        self.value = float(start_val)
        self.handle_radius = h // 2
        self.dragging = False

    def draw(self, surface, bar_color=(150,150,150), handle_color=(255,255,255)):
        pygame.draw.rect(surface, bar_color, self.rect)
        handle_x = int(self.rect.x + self.value * self.rect.width)
        pygame.draw.circle(surface, handle_color, (handle_x, self.rect.centery), self.handle_radius)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            # generous hit area around slider
            hit = pygame.Rect(self.rect.x - self.handle_radius,
                              self.rect.y - self.handle_radius,
                              self.rect.width + 2*self.handle_radius,
                              self.rect.height + 2*self.handle_radius)
            if hit.collidepoint(event.pos):
                self.dragging = True
        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            rx = max(self.rect.x, min(event.pos[0], self.rect.x + self.rect.width))
            self.value = (rx - self.rect.x) / self.rect.width

def options_menu(screen, get_font):
    clock = pygame.time.Clock()
    pygame.display.set_caption("Options")

    # background same as main
    original_bg = pygame.image.load("../graphics/main menu/Background.png")
    bg_height = original_bg.get_height()
    scale_factor = settings.WINDOW_HEIGHT / bg_height
    bg = pygame.transform.scale(original_bg, (int(original_bg.get_width() * scale_factor), settings.WINDOW_HEIGHT))
    bg_rect = bg.get_rect(center=(settings.WINDOW_WIDTH // 2, settings.WINDOW_HEIGHT // 2))

    # slider width centered, slight nudge left (small)
    slider_width = 300
    base_center_x = (settings.WINDOW_WIDTH - slider_width) // 2
    slider_x = base_center_x - 0   # Offset pos

    # initialize sliders from settings (persisted values)
    bgm_slider = Slider(slider_x, 200, slider_width, 18, getattr(settings, "BGM_VOLUME", 1.0))
    sfx_slider = Slider(slider_x, 300, slider_width, 18, getattr(settings, "SFX_VOLUME", 1.0))

    # back button (reuse your Button)
    back_btn = Button(None, (settings.WINDOW_WIDTH // 2, 500), "BACK", get_font(30), "black", "red")

    # preview sounds (optional)
    try:
        preview_bgm = pygame.mixer.Sound("../sounds/music.wav")
        preview_bgm.play(loops=-1)
        preview_bgm.set_volume(bgm_slider.value)
    except Exception:
        preview_bgm = None

    try:
        preview_sfx = pygame.mixer.Sound("../sounds/jump.wav")
    except Exception:
        preview_sfx = None

    running = True
    while running:
        screen.blit(bg, bg_rect.topleft)
        mouse_pos = pygame.mouse.get_pos()

        # draw labels aligned with slider_x
        screen.blit(get_font(24).render(f"BGM: {bgm_slider.value:.2f}", True, "black"), (slider_x, 160))
        screen.blit(get_font(24).render(f"SFX: {sfx_slider.value:.2f}", True, "black"), (slider_x, 260))

        bgm_slider.draw(screen)
        sfx_slider.draw(screen)

        back_btn.change_color(mouse_pos)
        back_btn.update(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            bgm_slider.handle_event(event)
            sfx_slider.handle_event(event)

            if event.type == pygame.MOUSEBUTTONDOWN:
                if back_btn.check_for_input(mouse_pos):
                    running = False

        # write values back into settings so they persist globally
        settings.BGM_VOLUME = bgm_slider.value
        settings.SFX_VOLUME = sfx_slider.value

        # update preview volume live
        if preview_bgm:
            preview_bgm.set_volume(settings.BGM_VOLUME)
        if preview_sfx and sfx_slider.dragging:
            preview_sfx.set_volume(settings.SFX_VOLUME)
            preview_sfx.play()

        pygame.display.update()
        clock.tick(60)

    # previews sounds 
    if preview_bgm:
        preview_bgm.stop()
