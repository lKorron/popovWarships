import pygame
import random
from config import config

class Ship:
    def __init__(self, color, speed=1, vision_range=3, attack_range=1, health=100, power=10, accuracy=0.7, attack_delay=30, flash_color=(255, 255, 0)):
        self.color = color
        self.base_color = color
        self.pos_x = None
        self.pos_y = None
        self.speed = speed
        self.vision_range = vision_range
        self.attack_range = attack_range
        self.health = health
        self.power = power
        self.accuracy = accuracy
        self.move_timer = 0
        self.attack_timer = 0
        self.attack_delay = attack_delay
        self.flash_color = flash_color
        self.flash_timer = 0
        self.flash_duration = 5

    def draw(self, x, y, screen, cell_size):
        pygame.draw.rect(screen, self.color, (x, y, cell_size, cell_size))

    def attack(self, target):
        if random.random() <= self.accuracy:
            target.health -= self.power
            target.flash_timer = target.flash_duration  # Запускаем таймер мигания
            if target.health <= 0:
                target.health = 0
                return True  # Цель уничтожена
        return False  # Цель не уничтожена

    def update(self):
        if self.flash_timer > 0:
            self.flash_timer -= 1
            self.color = self.flash_color if self.flash_timer % 2 == 0 else self.base_color
        else:
            self.color = self.base_color

    def calculate_strength(self, ships):
        strength = 0
        for ship in ships:
            strength += ship.health + ship.power
        return strength

    def get_available_directions(self, grid):
        directions = []
        if self.pos_x < grid.width - 1 and not grid.cells[self.pos_x + 1][self.pos_y]:
            directions.append("right")
        if self.pos_x > 0 and not grid.cells[self.pos_x - 1][self.pos_y]:
            directions.append("left")
        if self.pos_y > 0 and not grid.cells[self.pos_x][self.pos_y - 1]:
            directions.append("up")
        if self.pos_y < grid.height - 1 and not grid.cells[self.pos_x][self.pos_y + 1]:
            directions.append("down")
        return directions

    def choose_direction_based_on_vision(self, grid):
        ships_in_range = grid.find_ships_in_vision_range(self)
        if not ships_in_range:
            return self.get_random_direction(grid)

        friendly_ships = [ship for ship in ships_in_range if ship.ship_type == self.ship_type]
        enemy_ships = [ship for ship in ships_in_range if ship.ship_type != self.ship_type]

        if not enemy_ships:
            return self.get_random_direction(grid)

        friendly_strength = self.calculate_strength(friendly_ships) + self.calculate_strength([self])
        enemy_strength = self.calculate_strength(enemy_ships)

        friendly_strength += random.uniform(-0.1 * friendly_strength, 0.1 * friendly_strength)
        enemy_strength += random.uniform(-0.1 * enemy_strength, 0.1 * enemy_strength)

        if friendly_strength > enemy_strength:
            target_counts = {"right": 0, "left": 0, "up": 0, "down": 0}
            for target in enemy_ships:
                if target.pos_x > self.pos_x:
                    target_counts["right"] += 1
                elif target.pos_x < self.pos_x:
                    target_counts["left"] += 1
                if target.pos_y > self.pos_y:
                    target_counts["down"] += 1
                elif target.pos_y < self.pos_y:
                    target_counts["up"] += 1

            return self.get_available_direction(grid, target_counts, retreat=False)
        else:
            escape_counts = {"right": 0, "left": 0, "up": 0, "down": 0}
            for target in enemy_ships:
                if target.pos_x > self.pos_x:
                    escape_counts["left"] += 1
                elif target.pos_x < self.pos_x:
                    escape_counts["right"] += 1
                if target.pos_y > self.pos_y:
                    escape_counts["up"] += 1
                elif target.pos_y < self.pos_y:
                    escape_counts["down"] += 1

            return self.get_available_direction(grid, escape_counts, retreat=True)

    def get_random_direction(self, grid):
        directions = self.get_available_directions(grid)
        if directions:
            return random.choice(directions)
        return None

    def get_available_direction(self, grid, direction_counts, retreat):
        directions = [dir for dir, count in direction_counts.items() if count > 0]
        if not directions:
            return self.get_random_direction(grid)
        if retreat:
            return min(directions, key=lambda d: direction_counts[d])
        return max(directions, key=lambda d: direction_counts[d])

    def should_move_towards(self, target):
        distance_x = abs(self.pos_x - target.pos_x)
        distance_y = abs(self.pos_y - target.pos_y)
        return distance_x + distance_y > self.attack_range // 2


our_ship_color = config["our_ship_color"]
enemy_ship_color = config["enemy_ship_color"]


vision_range = config["vision_range"]
attack_range = config["attack_range"]

class OurShip(Ship):
    def __init__(self, color=our_ship_color, speed=1, vision_range=vision_range, attack_range=attack_range, health=100, power=10, accuracy=0.7, attack_delay=30):
        super().__init__(color, speed, vision_range, attack_range, health, power, accuracy, attack_delay)
        self.ship_type = "our"

class EnemyShip(Ship):
    def __init__(self, color=enemy_ship_color, speed=1, vision_range=vision_range, attack_range=attack_range, health=100, power=10, accuracy=0.7, attack_delay=30):
        super().__init__(color, speed, vision_range, attack_range, health, power, accuracy, attack_delay)
        self.ship_type = "enemy"