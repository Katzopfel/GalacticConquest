import pygame
import random
import Ship
import Planet
import Button
import AIController
import tkinter as tk
from tkinter import Text
import sys


# Initialize Pygame
pygame.init()
pygame.mixer.init()  # Initialize the mixer

# Load the background music
pygame.mixer.music.load("Music/2020-06-18_-_8_Bit_Retro_Funk_-_www.FesliyanStudios.com_David_Renda.mp3")  # Replace with your music file path
pygame.mixer.music.set_volume(0.5)  # Set volume (0.0 to 1.0)
pygame.mixer.music.play(-1)  # Play the music in a loop (-1 means loop indefinitely)

# Load win and lose music
win_music = "Music/8bit-ME_Victory01.mp3" 
lose_music = "Music/8-bit-video-game-lose-sound-version-1-145828.mp3" 

# Constants
SCREEN_WIDTH, SCREEN_HEIGHT = 1000, 800

SPACE_OFFSET_X = 50  # Space on the left side
SPACE_OFFSET_Y = 50  # Space on the top side
SPACE_OFFSET_RIGHT = 10  # Space on the right side
SPACE_OFFSET_BOTTOM = 150  # Space on the bottom side

GRID_SIZE = 10  # 10x10 grid
TILE_SIZE = 50

# Calculate total height and width for the grid including offsets
TOTAL_GRID_WIDTH = TILE_SIZE * GRID_SIZE + SPACE_OFFSET_X
TOTAL_GRID_HEIGHT = TILE_SIZE * GRID_SIZE + SPACE_OFFSET_Y + SPACE_OFFSET_BOTTOM

background_image = pygame.image.load("Space/Background_space.png")  # Update with your image path




PLANET_COUNT = 5
PLANET_IMAGES = ["Planets/Baren.png", "Planets/M3.png", "Planets/Ice.png","Planets/Lava.png","Planets/Terran.png","Planets/P1.png"]  # Add paths to your planet images
TURN_LIMIT = 30  # The maximum number of turns
current_turn = 0  # Start with turn 0

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255,0,0)
BLUE = (0,0,255)
YELLOW = (255,255,0)
ORANGE = (255,165,0)

colors = [RED, BLUE, GREEN, YELLOW, ORANGE]
planet_positions = []
planet_status = {} # Dictionary to track the status of each planet
font = pygame.font.Font(None, 24)  # Use a default font with size 24
font_small = pygame.font.Font(None, 20)  # Use a default font with size 24
log_messages = []  # List to store log messages
planet_messages = [] # List to store planet events
# Counters for planets conquered by each player
player_conquered_planets = 0
ai_conquered_planets = 0

#Buttons
move_button = Button.Button(200, 600, 200, 50, "Move", font, BLUE, RED)
upgrade_button = Button.Button(200, 650, 200, 50, "Upgrade", font, BLUE, RED)
conquer_button = Button.Button(200, 700, 200, 50, "Conquer", font, BLUE, RED) 
rules_button = Button.Button(450, 600, 100, 25, "Rules", font, BLUE, RED)


# Screen setup
screen = pygame.display.set_mode((TOTAL_GRID_WIDTH + SPACE_OFFSET_X,
                                   TOTAL_GRID_HEIGHT + SPACE_OFFSET_Y + SPACE_OFFSET_BOTTOM))
pygame.display.set_caption("Galactic Conquest Board")

# Tkinter rules window
def open_rules_window():
    root = tk.Tk()
    root.title("Game Rules")

    # Create a text widget to display/edit the rules
    text_widget = Text(root, height=15, width=50)
    text_widget.pack()

    # You can add default rules here
    default_rules = """Rules of Galactic Conquest:
    This is a turn by turn game. Each turn choose between "Move" "Upgrade" or "Conquer" (only if you are next to a planet).
    The goal of the game is, within the number of turn, either kill the enemy ship or if no one died, conquer the most amount of planets."""
    text_widget.insert(tk.END, default_rules)

    # Run the Tkinter event loop
    root.mainloop()


# Initialize planets
def initialize_planets():
    global planet_positions  # Use the global variable
    planets = []
    used_images = set() 

    while len(planets) < PLANET_COUNT:
        # Randomly select a position for the planet
        x, y = random.randint(0, GRID_SIZE - 1), random.randint(0, GRID_SIZE - 1)

        # Ensure no duplicate planets and exclude corners
        if (x, y) not in [(0, 0), (GRID_SIZE - 1, GRID_SIZE - 1)] and (x, y) not in [ (planet.x, planet.y) for planet in planets]:
            # Choose a random image for the planet, ensuring it's not used before
            available_images = list(set(PLANET_IMAGES) - used_images)  # Get unused images
            if available_images:
                image_path = random.choice(available_images)
                planet = Planet.Planet(x, y, image_path)  # Create a new planet instance
                planets.append(planet)
                used_images.add(image_path)  # Mark this image as used
                planet_status[(x, y)] = None  # Initially, the planet is unoccupied
            else:
                print("Not enough unique planet images available.")
                return  # Exit if not enough unique images
    planet_positions = planets  # Save the list of planet objects globally

# Draw the grid
def draw_grid():
    #screen.fill(BLACK)
    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            # Adjusted coordinates for grid placement to account for padding on all sides
            rect = pygame.Rect(col * TILE_SIZE + SPACE_OFFSET_X, row * TILE_SIZE + SPACE_OFFSET_Y, TILE_SIZE, TILE_SIZE)
            pygame.draw.rect(screen, WHITE, rect, 1)


# Draw planets on the grid
def draw_planets():
    for planet in planet_positions:
        planet.draw(screen, TILE_SIZE)

# Initialize the board with planets and ships
def initialize_board(player_ship, ai_ship, turn_indicator, remaining_turns, upgrade_message):
    screen.blit(background_image, (0, 0))  # Draw the background image
    draw_grid()
    draw_planets()  # Call the function without parameters to draw the global planet positions
    player_ship.draw(screen, TILE_SIZE)  # Draw player ship
    ai_ship.draw(screen, TILE_SIZE)      # Draw AI ship

    draw_health(player_ship, ai_ship)

    # Draw turn indicator
    turn_text = f"{turn_indicator} - {remaining_turns} turns left"
    text = font.render(turn_text, True, WHITE)
    text_rect = text.get_rect(center=(SCREEN_WIDTH // 2.2, 20))  # Centered at the top
    screen.blit(text, text_rect)  # Draw the text

     # Show number of planets conquered by each player
    player_planets_text = font_small.render(f"Player Conquered Planets: {player_conquered_planets}", True, WHITE)
    ai_planets_text = font_small.render(f"AI Conquered Planets: {ai_conquered_planets}", True, WHITE)
    screen.blit(player_planets_text, (10, 610))  # Position below health
    screen.blit(ai_planets_text, (10, 635))      # Position below player planets


    # Draw the buttons after the grid
    move_button.draw(screen)
    upgrade_button.draw(screen)
    rules_button.draw(screen)  # Draw the rules button

    for i, message in enumerate(log_messages[-5:]):  # Show the last 5 messages
        log_text = font.render(message, True, WHITE)
        screen.blit(log_text, (0, 700 + move_button.height + (i * 20)))  # Adjust position

    pygame.display.update()

def draw_text(text, font, color, surface, x, y):
    textobj = font.render(text, True, color)
    textrect = textobj.get_rect()
    textrect.topleft = (x, y)
    surface.blit(textobj, textrect)

# Draw health information
def draw_health(player_ship, ai_ship, upgrade_message=""):
    player_health_text = font.render(f"Player Health: {player_ship.health}", True, WHITE)
    ai_health_text = font.render(f"AI Health: {ai_ship.health}", True, WHITE)
    screen.blit(player_health_text, (10,10))  # Move player health text more to the left
    screen.blit(ai_health_text, (10,30))  # Move AI health text more to the left

    # Draw upgrade message if available
    if upgrade_message:
        upgrade_text = font.render(upgrade_message, True, GREEN)
        screen.blit(upgrade_text, (10, 50))  # Positioning below health


def check_if_destroyed(player_ship,ai_ship):
    # Check if ships are destroyed and display message
        if player_ship.is_destroyed() or ai_ship.is_destroyed():
            running = False  # End game if a ship is destroyed
            
            # Prepare to display the game over message
            font = pygame.font.SysFont(None, 74)
            screen.fill((0, 0, 0))  # Clear screen before displaying text
            if player_ship.is_destroyed():
                draw_text("AI Ship Wins!", font, (255, 0, 0), screen, 200, 300)
            if ai_ship.is_destroyed():
                draw_text("Player Ship Wins!", font, (0, 255, 0), screen, 200, 300)
            pygame.display.update()
            pygame.time.delay(3000)  # Show message for 3 seconds
            return running

def check_collisions(player_ship,ai_ship):
    # Check for collision (example logic; modify as needed)
        if player_ship.x == ai_ship.x and player_ship.y == ai_ship.y:
            damage = 20  # Example damage value
            player_ship.take_damage(damage)
            ai_ship.take_damage(damage)
    


# Function to display the action menu
def show_action_menu(player_ship,ai_ship,remaining,planets):
    global log_messages
    conquer_button_clicked=False
    running = True
    while running:
        screen.fill(BLACK)
        initialize_board(player_ship, ai_ship, "Player's Turn", remaining, upgrade_message="")
        planet = is_ship_next_to_planet(player_ship,planets)  # Check if the player is next to a planet
        
        # Draw the buttons
        move_button.draw(screen)
        upgrade_button.draw(screen)
        rules_button.draw(screen)

        if is_ship_next_to_planet(player_ship,planets):
            conquer_button.draw(screen)

        pygame.display.flip()
        
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            
            # Handle button clicks only on MOUSEBUTTONDOWN
            if event.type == pygame.MOUSEBUTTONDOWN:
                if move_button.is_clicked():
                    print("Move selected")
                    return "move"
                elif upgrade_button.is_clicked():
                    print("Upgrade selected")
                    return "upgrade"
                elif conquer_button.is_clicked() and not conquer_button_clicked:
                    conquer_button_clicked = True  # Set the flag to avoid multiple clicks
                    print("Conquer selected")
                    return "conquer"
                elif rules_button.is_clicked():
                    open_rules_window()
        
            # Reset the flag on MOUSEBUTTONUP
            if event.type == pygame.MOUSEBUTTONUP:
                conquer_button_clicked = False  # Allow conquer button to be clicked again
        
        pygame.time.Clock().tick(30)

# Move logic function
def move(player_ship,ai_ship,player,planets,remaining,upgrade_message="",):
    global log_messages
    moving = True
    
    while moving:
        screen.fill(BLACK)  # Clear the screen
        initialize_board(player_ship, ai_ship, "Player's Turn", remaining, upgrade_message="")

        # Draw the player's ship
        player_ship.draw(screen,TILE_SIZE)


        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            if event.type == pygame.KEYDOWN:
                dx, dy = 0, 0  # Initialize movement

                if event.key == pygame.K_LEFT:
                    dx = -1
                elif event.key == pygame.K_RIGHT:
                    dx = 1
                elif event.key == pygame.K_UP:
                    dy = -1
                elif event.key == pygame.K_DOWN:
                    dy = 1

                # Move the player's ship and stop the move phase
                if dx != 0 or dy != 0:
                    player_ship.move(dx, dy, GRID_SIZE,planets, log_messages)
                    if player == True :
                        log_messages.append("Player moved")
                    moving = False

        player_ship.draw(screen,TILE_SIZE)  # Redraw the player's ship
        pygame.display.update()  # Update the display
        pygame.time.Clock().tick(60)  # Frame rate cap

# Function to check if a ship is next to a planet
def is_ship_next_to_planet(ship,planets):
    # Round positions to avoid small positional flickers
    player_x, player_y = round(ship.x), round(ship.y)
    # Define proximity radius
    for planet in planets:
        if abs(planet.x - player_x) <= 1 and abs(planet.y - player_y) <= 1:
            return planet
    return None


def conquer_planet(player_ship, planet_positions, log_messages):
    global player_conquered_planets  # Make sure to use the global variable to keep track of conquered planets

    # Check if the player ship is next to a planet
    planet = is_ship_next_to_planet(player_ship,planet_positions)
    
    if planet:
        planet_key = (planet.x, planet.y)  # Key for checking planet status

        # Check if the planet is not already occupied
        if planet_status[planet_key] is None:
            # Conquer the planet
            planet_status[planet_key] = 'occupied'  # Mark the planet as occupied
            player_conquered_planets += 1  # Increment the conquered planets counter
            log_messages.append(f"Player conquered the planet at ({planet.x}, {planet.y}). Total conquered: {player_conquered_planets}")
        else:
            log_messages.append(f"Planet at ({planet.x}, {planet.y}) is already occupied.")
    else:
        log_messages.append("No planet next to the ship to conquer.")       
        

# Function to handle the end of the game based on health or turns
def check_game_end(player_ship, ai_ship, player_conquered_planets, ai_conquered_planets, current_turn, TURN_LIMIT):
    if player_ship.health <= 0:
        return "Enemy wins! Player ship was destroyed."
    elif ai_ship.health <= 0:
        return "Player wins! Enemy ship was destroyed."
    elif current_turn >= TURN_LIMIT:
        if player_conquered_planets > ai_conquered_planets:
            return "Player wins by conquering more planets!"
        elif ai_conquered_planets > player_conquered_planets:
            return "Enemy wins by conquering more planets!"
        else:
            return "It's a tie! Both sides conquered the same number of planets."
    return None  # Continue the game

def get_font_for_message(message, base_size=74, max_width=400):
    """Adjust the font size based on the message length to fit the screen."""
    font_size = base_size
    font = pygame.font.SysFont(None, font_size)
    text_surface = font.render(message, True, (255, 255, 0))
    
    # Reduce font size until the text fits within the maximum width
    while text_surface.get_width() > max_width and font_size > 10:  # Minimum font size of 10
        font_size -= 2
        font = pygame.font.SysFont(None, font_size)
        text_surface = font.render(message, True, (255, 255, 0))

    return font



# Main function to initialize and display the board
def main():
    running = True
    clock = pygame.time.Clock()
    player_turn = True
    upgrade_message = ""
    conquered_planets = {}
    stage = "menu" #Game starts with a menu
    global log_messages
    global planet_messages
    global current_turn
    global ai_conquered_planets


    player_ship = Ship.PlayerShip(0, GRID_SIZE-1)
    ai_ship = Ship.AIShip(GRID_SIZE-1, 0)
    initialize_planets()
    initialize_board(player_ship, ai_ship, "Player's Turn", TURN_LIMIT, upgrade_message="")


    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

            # Handle button clicks
            if event.type == pygame.MOUSEBUTTONDOWN:
                if rules_button.is_clicked():
                    open_rules_window()  # Open the rules window when the button is clicked



        if player_turn:

            initialize_board(player_ship, ai_ship,"Player's Turn" if player_turn else "AI's Turn", TURN_LIMIT - current_turn, upgrade_message)
            action = show_action_menu(player_ship, ai_ship,TURN_LIMIT - current_turn,planet_positions)  # Show the action menu and get the player's choice

            if action == "move":
                move(player_ship,ai_ship,True,planet_positions,TURN_LIMIT - current_turn,upgrade_message)
                player_turn = False  # End the player's turn after making a choice

            elif action == "upgrade":
                log_messages.append("Player upgraded their ship.")
                player_ship.upgrade()  # Call the upgrade method on the player ship
                log_messages.append("Upgraded Defense!: {}".format(player_ship.defense))  # Show upgrade message
                player_turn = False  # End the player's turn after making a choice
            elif action == "conquer":
                conquer_planet(player_ship,planet_positions,log_messages)
                player_turn = False
            else:
                print("No planet next to the ship!")
            player_turn = False
            current_turn += 1

                

        else:  # AI's turn
            # AI behavior based on health and position
            if ai_ship.health < 30 and player_ship.health > ai_ship.health:
                # If the AI's health is low, it should upgrade first
                ai_ship.upgrade()
                log_messages.append("Enemy upgraded their ship for defense.")
                log_messages.append("Enemy's defense is now {}".format(ai_ship.defense))
            else:
                # Move towards player ship if it's not close
                if abs(ai_ship.x - player_ship.x) > 1 or abs(ai_ship.y - player_ship.y) > 1:
                    AIController.ai_move_toward(ai_ship, player_ship.x, player_ship.y, GRID_SIZE, planet_positions, log_messages)
                    log_messages.append("Enemy moved toward the player.")
                else:
                    # If adjacent to the player, decide randomly to attack or conquer a planet
                    if random.choice([True, False]):  # Randomly decide to attack or not
                        attack_message = AIController.ai_attack(ai_ship, player_ship)  # AI attacks
                        log_messages.append(attack_message)
                    else:
                        if not AIController.ai_conquer_if_possible(ai_ship, planet_positions, log_messages, planet_status):
                            log_messages.append("Enemy did not conquer any planets.")
                        else:
                            ai_conquered_planets += 1

            player_turn = True  # End AI turn and give control to the player

      
        if current_turn >= TURN_LIMIT:
            if player_ship.health > ai_ship.health:
                log_messages.append("Player wins by health!")
                running = False
            elif player_ship.health < ai_ship.health:
                log_messages.append("Enemy wins by health!")
                running = False
            else:
                log_messages.append("It's a tie!")
                running = False

        clock.tick(30)  # Control the frame rate
               
        check_collisions(player_ship,ai_ship)

        initialize_board(player_ship, ai_ship,"Player's Turn" if player_turn else "AI's Turn", TURN_LIMIT - current_turn, upgrade_message)

        # Check if the game should end based on health or turns
        result_message = check_game_end(player_ship, ai_ship, player_conquered_planets, ai_conquered_planets, current_turn, TURN_LIMIT)

        if result_message:
            # Display the end game message on the screen
            screen.fill(BLACK)  # Clear the screen before displaying text
    
            # Get the appropriate font for the result message
            font = get_font_for_message(result_message)
            lost = None
    
            # Draw the result message at the center
            if result_message=="Enemy wins! Player ship was destroyed" or result_message=="Enemy wins by conquering more planets!":
                lost=1
            elif result_message == "It's a tie! Both sides conquered the same number of planets.":
                lost=2
            elif result_message == "Player wins! Enemy ship was destroyed." or result_message== "Player wins by conquering more planets!":
                lost = 0

            if lost == 0:
                pygame.mixer.music.stop()  # Stop background music
                pygame.mixer.music.load(win_music)  # Load win music
                pygame.mixer.music.play()  # Play win music
            elif lost == 1 :
                # Player lost
                pygame.mixer.music.stop()  # Stop background music
                pygame.mixer.music.load(lose_music)  # Load lose music
                pygame.mixer.music.play()  # Play lose music

            draw_text(result_message, font, (255, 255, 0), screen, (SCREEN_WIDTH - font.size(result_message)[0]) // 2-200, SCREEN_HEIGHT // 2)
    
            pygame.display.update()
            # Wait for the player to close the window
            waiting = True
            while waiting:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        waiting = False  # Exit the loop and allow the window to close
            running = False


        


    pygame.quit()




# If this file is run directly, start the game board initialization
if __name__ == "__main__":
    main()