import pygame
import sys
from functools import lru_cache
from button import Button
from settings import WINDOW_WIDTH, WINDOW_HEIGHT
from options import options_menu

# --- Initialize ---
pygame.init()
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Menu")

# --- Constants ---
WHITE = "White"
BLACK = "Black"
GREEN = "Green"
RED = "Red"
GOLD = "#b68f40"
LIGHT_GREEN = "#d7fcd4"

# --- Background setup ---
original_bg = pygame.image.load("../graphics/main menu/Background.png")
bg_height = original_bg.get_height()
scale_factor = WINDOW_HEIGHT / bg_height

bg = pygame.transform.scale(
    original_bg,
    (int(original_bg.get_width() * scale_factor), WINDOW_HEIGHT)
)
bg_rect = bg.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))

# --- Cached fonts ---
@lru_cache(maxsize=10)
def get_font(size):
    return pygame.font.Font("../graphics/main menu/font.ttf", int(size * scale_factor))

# --- Button image loader ---
def load_button_image(path):
    return pygame.transform.scale(
        pygame.image.load(path),
        (int(240 * scale_factor), int(60 * scale_factor))
    )

# --- Load images once ---
play_img = load_button_image("../graphics/main menu/Play Rect.png")
options_img = load_button_image("../graphics/main menu/Options Rect.png")
quit_img = load_button_image("../graphics/main menu/Quit Rect.png")

# --- Back button factory ---
def draw_back_button(text_color, hover_color, font_size):
    return Button(
        None,
        (WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2 + 80),
        "BACK",
        get_font(font_size),
        text_color,
        hover_color
    )

# --- Reusable message screen ---
def render_back_screen(bg_color, message, text_color=WHITE, font_size=20):
    while True:
        screen.fill(bg_color)
        msg_text = get_font(font_size).render(message, True, text_color)
        msg_rect = msg_text.get_rect(center=(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2 - 80))
        screen.blit(msg_text, msg_rect)

        back_btn = draw_back_button(text_color, RED if bg_color == BLACK else GREEN, 30)
        mouse_pos = pygame.mouse.get_pos()
        back_btn.change_color(mouse_pos)
        back_btn.update(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN and back_btn.check_for_input(mouse_pos):
                return

        pygame.display.update()

# --- Placeholder & options screens ---
def placeholder_level(message):
    render_back_screen(BLACK, message)

def options():
    options_menu(screen, get_font)

# --- Level launcher ---
def launch_level(level_number):
    level_messages = {
        1: "Level 1 Coming Soon!",
    }
    if level_number in level_messages:
        placeholder_level(level_messages[level_number])
    elif level_number == 2:
        from game_level2 import Game
        Game().run()
    elif level_number == 3:
        from game_level3 import Game
        Game().run()

# --- Level select screen ---
def play():
    def create_level_buttons():
        labels = ["LEVEL 1", "LEVEL 2", "LEVEL 3", "BACK"]
        colors = [GREEN, GREEN, GREEN, RED]
        actions = [1, 2, 3, "back"]
        return [
            (Button(None, (WINDOW_WIDTH / 2, (160 + i * 80) * scale_factor),
                    label, get_font(20), WHITE, color), level_action)
            for i, (label, color, level_action) in enumerate(zip(labels, colors, actions))
        ]

    while True:
        screen.fill(BLACK)
        mouse_pos = pygame.mouse.get_pos()

        title = get_font(25).render("Select a Level", True, WHITE)
        screen.blit(title, title.get_rect(center=(WINDOW_WIDTH / 2, 80 * scale_factor)))

        level_buttons = create_level_buttons()

        for button, _ in level_buttons:
            button.change_color(mouse_pos)
            button.update(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                for button, action in level_buttons:
                    if button.check_for_input(mouse_pos):
                        if action == "back":
                            return
                        else:
                            launch_level(action)

        pygame.display.update()

# --- Main menu screen ---
def main_menu():
    pygame.display.set_caption("Menu")

    while True:
        screen.blit(bg, bg_rect.topleft)
        mouse_pos = pygame.mouse.get_pos()

        title = get_font(40).render("MAIN MENU", True, GOLD)
        screen.blit(title, title.get_rect(center=(WINDOW_WIDTH / 2, 80 * scale_factor)))

        buttons = [
            Button(play_img, (WINDOW_WIDTH / 2, 200 * scale_factor), "PLAY", get_font(30), LIGHT_GREEN, WHITE),
            Button(options_img, (WINDOW_WIDTH / 2, 300 * scale_factor), "OPTIONS", get_font(30), LIGHT_GREEN, WHITE),
            Button(quit_img, (WINDOW_WIDTH / 2, 400 * scale_factor), "QUIT", get_font(30), LIGHT_GREEN, WHITE)
        ]

        for button in buttons:
            button.change_color(mouse_pos)
            button.update(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if buttons[0].check_for_input(mouse_pos):
                    play()
                elif buttons[1].check_for_input(mouse_pos):
                    options()
                elif buttons[2].check_for_input(mouse_pos):
                    pygame.quit()
                    sys.exit()

        pygame.display.update()

# --- Run main menu ---
if __name__ == "__main__":
    main_menu()
