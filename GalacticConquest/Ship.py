import pygame
from Board import *
import random

# Constants for ship colors (optional, if you use an image)
BLUE = (0, 0, 255)  # Player ship color
RED = (255, 0, 0)   # AI ship color
Player_path = "Ships/Player/Player Ship.png"
AI_path = "Ships/AI/AlienShip.png"


import pygame

class Ship:
    def __init__(self, x, y, images, health, defense, max_health, max_defense):
        self.x = x
        self.y = y
        self.health = health
        self.defense = defense
        self.max_health = 0
        self.max_defense=0
        self.images= images
        self.current_image = self.images['up']  # Default image


    def move(self, dx, dy, grid_size,planets,logs):
        new_x = self.x + dx
        new_y = self.y + dy

        # Check if the new position is within grid bounds
        if 0 <= new_x < grid_size and 0 <= new_y < grid_size:
            

            # Move the ship if the destination is valid
            self.x = new_x
            self.y = new_y

            # Update current image based on direction
            if dy < 0:
                self.current_image = self.images['up']
            elif dy > 0:
                self.current_image = self.images['down']
            elif dx < 0:
                self.current_image = self.images['left']
            elif dx > 0:
                self.current_image = self.images['right']

    def take_damage(self, damage):
        # Calculate effective damage considering defense
        effective_damage = max(damage - self.defense, 0)
        self.health -= effective_damage

    def upgrade(self):
        rand= random.randint(1, 5)
        self.defense += rand  # Increase defense by a random number between 1 and 5
        if self.defense >= 10:  # Cap defense at max def
            self.defense = 10

    def is_destroyed(self):
        return self.health <= 0

    def draw(self, screen, tile_size):
        # Display health
        health_text = f"Health: {self.health}"
        font = pygame.font.SysFont(None, 24)
        text_surface = font.render(health_text, True, (255, 255, 255))
        screen.blit(self.current_image, (self.x * tile_size + SPACE_OFFSET_X, self.y * tile_size + SPACE_OFFSET_Y))



class PlayerShip(Ship):
    def __init__(self, x, y):
        images = {
            'up': pygame.image.load("Ships/Player/Playership_up.png"),
            'down': pygame.image.load("Ships/Player/Playership_down.png"),
            'left': pygame.image.load("Ships/Player/Playership_left.png"),
            'right': pygame.image.load("Ships/Player/Playership_right.png"),
        }
        super().__init__(x, y, images, health=100, defense=10, max_health=100, max_defense=10)
        


class AIShip(Ship):
    def __init__(self, x, y):
        images = {
            'up': pygame.image.load("Ships/AI/AlienShip.png"),
            'down': pygame.image.load("Ships/AI/AlienShip.png"),
            'left': pygame.image.load("Ships/AI/AlienShip.png"),
            'right': pygame.image.load("Ships/AI/AlienShip.png"),
        }
        super().__init__(x, y, images, health=80, defense=5, max_health=80, max_defense=5)







