import pygame
import random
from config import config

class Ship:
    def __init__(self, color, speed=1, vision_range=3, attack_range=1, health=100, power=10, accuracy=0.7, attack_delay=30, direction="up"):
        self.color = color
        self.base_color = color  # Основной цвет корабля
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
        self.attack_delay = attack_delay  # Задержка между атаками
        self.flash_timer = 0
        self.flash_duration = 5  # Продолжительность мигания
        self.direction = direction  # Направление корабля по умолчанию

    def draw(self, x, y, screen, cell_size):
        half_size = cell_size // 2
        if self.direction == "up":
            points = [(x + half_size, y), (x, y + cell_size), (x + cell_size, y + cell_size)]
        elif self.direction == "down":
            points = [(x + half_size, y + cell_size), (x, y), (x + cell_size, y)]
        elif self.direction == "left":
            points = [(x, y + half_size), (x + cell_size, y), (x + cell_size, y + cell_size)]
        else:  # right
            points = [(x + cell_size, y + half_size), (x, y), (x, y + cell_size)]
        pygame.draw.polygon(screen, self.color, points)

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
            self.color = config["flash_color"] if self.flash_timer % 2 == 0 else self.base_color
        else:
            self.color = self.base_color

    def calculate_strength(self, ships):
        strength = 0
        for ship in ships:
            strength += ship.health + ship.power
        return strength

    def turn_left(self):
        directions = ["up", "left", "down", "right"]
        self.direction = directions[(directions.index(self.direction) + 1) % 4]

    def turn_right(self):
        directions = ["up", "right", "down", "left"]
        self.direction = directions[(directions.index(self.direction) + 1) % 4]

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

class Destroyer(OurShip, EnemyShip):
    def __init__(self, ship_type):
        if ship_type == "our":
            OurShip.__init__(self, color=(0, 0, 255), speed=50, vision_range=4, attack_range=3, health=80, power=10,
                             accuracy=0.7)
        else:
            EnemyShip.__init__(self, color=(255, 0, 0), speed=50, vision_range=4, attack_range=3, health=80,
                               power=10, accuracy=0.75)
        self.ship_type = ship_type


class LightCruiser(OurShip, EnemyShip):
    def __init__(self, ship_type):
        if ship_type == "our":
            OurShip.__init__(self, color=(0, 0, 255), speed=40, vision_range=5, attack_range=4, health=120, power=15,
                             accuracy=0.75)
        else:
            EnemyShip.__init__(self, color=(255, 0, 0), speed=40, vision_range=5, attack_range=4, health=120, power=15,
                               accuracy=0.75)
        self.ship_type = ship_type


class HeavyCruiser(OurShip, EnemyShip):
    def __init__(self, ship_type):
        if ship_type == "our":
            OurShip.__init__(self, color=(0, 0, 255), speed=35, vision_range=5, attack_range=4, health=150, power=20,
                             accuracy=0.75)
        else:
            EnemyShip.__init__(self, color=(255, 0, 0), speed=35, vision_range=5, attack_range=4, health=150, power=20,
                               accuracy=0.75)
        self.ship_type = ship_type


class BattleCruiser(OurShip, EnemyShip):
    def __init__(self, ship_type):
        if ship_type == "our":
            OurShip.__init__(self, color=(0, 0, 255), speed=30, vision_range=6, attack_range=5, health=150, power=25,
                             accuracy=0.8)
        else:
            EnemyShip.__init__(self, color=(255, 0, 0), speed=30, vision_range=6, attack_range=5, health=150, power=25,
                               accuracy=0.8)
        self.ship_type = ship_type


class Battleship(OurShip, EnemyShip):
    def __init__(self, ship_type):
        if ship_type == "our":
            OurShip.__init__(self, color=(0, 0, 255), speed=20, vision_range=7, attack_range=6, health=200, power=30,
                             accuracy=0.8)
        else:
            EnemyShip.__init__(self, color=(255, 0, 0), speed=20, vision_range=7, attack_range=6, health=200, power=30,
                               accuracy=0.8)
        self.ship_type = ship_type


class AircraftCarrier(OurShip, EnemyShip):
    def __init__(self, ship_type):
        if ship_type == "our":
            OurShip.__init__(self, color=(0, 0, 255), speed=10, vision_range=8, attack_range=7, health=200, power=35,
                             accuracy=0.8)
        else:
            EnemyShip.__init__(self, color=(255, 0, 0), speed=10, vision_range=8, attack_range=7, health=200,
                               power=35, accuracy=0.8)
        self.ship_type = ship_type