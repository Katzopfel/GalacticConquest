import pygame
import random
import Ship
import Planet
import Button
import Board

def ai_decision(ai_ship, player_ship, planet_positions, log_messages,stat):
    global ai_conquered_planets

    # Check if AI is next to a conquered planet
    for planet in planet_positions:
        if stat.get((planet.x, planet.y)) == "AI":  # Check if the planet is conquered by AI
            if abs(ai_ship.x - planet.x) <= 1 and abs(ai_ship.y - planet.y) <= 1:
                log_messages.append(f"AI is next to its conquered planet at ({planet.x}, {planet.y}) and will not move.")
                return  # Exit the function if AI is next to a conquered planet

    # Find closest planet
    closest_planet = None
    min_distance = float('inf')
    for planet in planet_positions:
        if stat.get((planet.x, planet.y)) is None:  # Only consider unoccupied planets
            distance = abs(ai_ship.x - planet.x) + abs(ai_ship.y - planet.y)
            if distance < min_distance:
                min_distance = distance
                closest_planet = planet

    # Check if AI is close to a planet
    if closest_planet and min_distance <= 1:
        # Only conquer if the planet is unoccupied
        if stat.get((closest_planet.x, closest_planet.y)) is None:
            Board.conquer_planet(ai_ship, planet_positions, log_messages)
            log_messages.append(f"AI conquered planet at ({closest_planet.x}, {closest_planet.y})")
            Board.ai_conquered_planets += 1  # Increment counter here
        return

    # AI will move towards the closest planet or the player if no planet nearby
    if closest_planet and min_distance > 1:
        target_x = closest_planet.x
        target_y = closest_planet.y
    else:
        target_x = player_ship.x
        target_y = player_ship.y

    # AI movement logic to move towards the target
    dx = 1 if ai_ship.x < target_x else -1 if ai_ship.x > target_x else 0
    dy = 1 if ai_ship.y < target_y else -1 if ai_ship.y > target_y else 0
    ai_ship.move(dx, dy, Board.GRID_SIZE, planet_positions, log_messages)
    log_messages.append(f"AI moved towards {'planet' if closest_planet else 'player'}")
    
    # AI may upgrade if it's far from any planet or player
    if random.random() < 0.2:  # Add some randomness to AI's decision to upgrade
        ai_ship.upgrade()
        log_messages.append("AI upgraded its ship.")



# AI can make decisions to engage or avoid the player based on health
def ai_engage_or_avoid(ai_ship, player_ship, pos,log_messages):
    distance_to_player = abs(ai_ship.x - player_ship.x) + abs(ai_ship.y - player_ship.y)
    
    if distance_to_player <= 2:  # AI close to the player
        if ai_ship.health > player_ship.health:
            log_messages.append("AI engages the player!")
            dx = 1 if ai_ship.x < player_ship.x else -1 if ai_ship.x > player_ship.x else 0
            dy = 1 if ai_ship.y < player_ship.y else -1 if ai_ship.y > player_ship.y else 0
            ai_ship.move(dx, dy, Board.GRID_SIZE, pos, log_messages)
        else:
            log_messages.append("AI retreats to avoid the player!")
            dx = -1 if ai_ship.x < player_ship.x else 1
            dy = -1 if ai_ship.y < player_ship.y else 1
            ai_ship.move(dx, dy, Board.GRID_SIZE, pos, log_messages)

def ai_move_toward(ship, target_x, target_y, grid_size,pos,logs):
    """Moves the AI ship toward the target coordinates."""
    if ship.x < target_x:
        ship.move(1, 0, grid_size, pos, logs)
    elif ship.x > target_x:
        ship.move(-1, 0, grid_size, pos, logs)

    if ship.y < target_y:
        ship.move(0, 1, grid_size, pos, logs)
    elif ship.y > target_y:
        ship.move(0, -1, grid_size, pos, logs)

def ai_conquer_if_possible(ai_ship, planet_positions, log_messages,stat):
    """AI tries to conquer a planet if it's next to one."""
    for planet in planet_positions:
        if abs(ai_ship.x - planet.x) <= 1 and abs(ai_ship.y - planet.y) <= 1:
            if stat.get((planet.x, planet.y)) is None:  # If unoccupied
                stat[(planet.x, planet.y)] = "AI"  # Conquer it
                log_messages.append(f"AI conquered planet at ({planet.x}, {planet.y})")
                
                return True
    return False


def ai_attack(ai_ship, player_ship):
    # Define damage value
    damage = 20  # or whatever damage value you deem appropriate
    player_ship.take_damage(damage)
    return f"AI attacks! Player ship takes {damage} damage."