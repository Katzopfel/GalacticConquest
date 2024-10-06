import pygame

class Button:
    def __init__(self, x, y, width, height, text, font, color, hover_color):
        self.x=x
        self.y=y
        self.rect = pygame.Rect(x, y, width, height)
        self.height=height
        self.text = text
        self.font = font
        self.color = color
        self.hover_color = hover_color
        self.clicked = False

    def draw(self, screen):
        # Change color on hover
        mouse_pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(mouse_pos):
            pygame.draw.rect(screen, self.hover_color, self.rect)
        else:
            pygame.draw.rect(screen, self.color, self.rect)

        # Render the button text
        text_surface = self.font.render(self.text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    def is_clicked(self):
        # Check if button is clicked
        mouse_pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(mouse_pos):
            if pygame.mouse.get_pressed()[0]:  # Left click
                return True
        return False
    
    