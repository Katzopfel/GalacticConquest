import pygame



class Planet:
    def __init__(self, x, y, image_path):
        self.x = x
        self.y = y
        self.image = pygame.image.load(image_path)  # Load the planet image
        self.image = pygame.transform.scale(self.image, (40, 40))  # Adjust the size of the image

    def draw(self, surface, tile_size):
        # Draw the planet on the given surface at its grid position
        surface.blit(self.image, (self.x * tile_size + 50 + tile_size // 2 - 20, 
                                   self.y * tile_size + 50 + tile_size // 2 - 20))

