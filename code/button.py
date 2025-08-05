import pygame

class Button:
    def __init__(self, image, pos, text_input, font, base_color, hovering_color):
        """
        Initialize a button with optional image and text.

        Args:
            image (Surface or None): Background image for the button.
            pos (tuple): (x, y) center position.
            text_input (str): Text to display.
            font (pygame.font.Font): Font object.
            base_color (str or tuple): Normal text color.
            hovering_color (str or tuple): Color when hovered.
        """
        self.image = image
        self.x_pos, self.y_pos = pos
        self.font = font
        self.base_color = base_color
        self.hovering_color = hovering_color
        self.text_input = text_input

        self.text = self.font.render(self.text_input, True, self.base_color)
        if self.image is None:
            self.image = self.text

        self.rect = self.image.get_rect(center=(self.x_pos, self.y_pos))
        self.text_rect = self.text.get_rect(center=(self.x_pos, self.y_pos))

    def update(self, screen):
        """Draw the button and its text to the screen."""
        if self.image:
            screen.blit(self.image, self.rect)
        screen.blit(self.text, self.text_rect)

    def check_for_input(self, position):
        """Return True if the mouse is over the button."""
        return self.rect.collidepoint(position)

    def change_color(self, position):
        """Update text color based on hover state."""
        color = self.hovering_color if self.rect.collidepoint(position) else self.base_color
        self.text = self.font.render(self.text_input, True, color)
