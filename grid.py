import pygame
import random

class Grid:
    def __init__(self, width, height, cell_size, grid_color=(255, 255, 255)):
        self.width = width
        self.height = height
        self.cell_size = cell_size
        self.grid_color = grid_color
        self.cells = [[None for _ in range(height)] for _ in range(width)]

    def draw(self, screen):
        for x in range(0, self.width * self.cell_size, self.cell_size):
            for y in range(0, self.height * self.cell_size, self.cell_size):
                rect = pygame.Rect(x, y, self.cell_size, self.cell_size)
                pygame.draw.rect(screen, self.grid_color, rect, 1)

    def add_ship_from_coords(self, x, y, ship):
        grid_x = x // self.cell_size
        grid_y = y // self.cell_size
        if self.cells[grid_x][grid_y] is None:
            self.cells[grid_x][grid_y] = ship
            ship.pos_x = grid_x
            ship.pos_y = grid_y

    def add_ship_from_cell(self, cell_x, cell_y, ship):
        if self.cells[cell_x][cell_y] is None:
            self.cells[cell_x][cell_y] = ship
            ship.pos_x = cell_x
            ship.pos_y = cell_y

    def delete_ship(self, cell_x, cell_y):
        self.cells[cell_x][cell_y] = None

    def move_ship2position(self, ship, position):
        cell_x, cell_y = position

        if self.cells[cell_x][cell_y] is None:
            ship_x = ship.pos_x
            ship_y = ship.pos_y
            self.delete_ship(ship_x, ship_y)
            self.add_ship_from_cell(cell_x, cell_y, ship)

    def move_ship(self, ship):
        direction = ship.direction
        if direction == "right" and self.width - 1 > ship.pos_x:
            self.move_ship2position(ship, (ship.pos_x + 1, ship.pos_y))
        elif direction == "left" and 0 < ship.pos_x:
            self.move_ship2position(ship, (ship.pos_x - 1, ship.pos_y))
        elif direction == "up" and 0 < ship.pos_y:
            self.move_ship2position(ship, (ship.pos_x, ship.pos_y - 1))
        elif direction == "down" and self.height - 1 > ship.pos_y:
            self.move_ship2position(ship, (ship.pos_x, ship.pos_y + 1))

    def move_ship_randomly(self, ship):


        available_directions = ship.get_available_directions(self)

        if ship.direction in available_directions:
            actions = ["rotate", "forward"]
            if random.choice(actions) == "rotate":
                self.rotate_ship_randomly(ship)
            else:
                self.move_ship(ship)

        else:
            self.rotate_ship_randomly(ship)


    def rotate_ship_randomly(self, ship):
        ship.turn_left() if random.choice(["turn_left", "turn_right"]) == "turn_left" else ship.turn_right()

    def spawn_ships(self, ship, ships_count=5):
        height_lower = 0
        height_upper = self.height - 1

        if ship.ship_type == "our":
            height_lower = self.height / 2
            height_upper = self.height - 1

        if ship.ship_type == "enemy":
            height_lower = 0
            height_upper = self.height / 2 - 1

        coords = set()

        while len(coords) < ships_count:
            cell_x = random.randint(0, self.width - 1)
            cell_y = random.randint(height_lower, height_upper)

            if (cell_x, cell_y) not in coords:
                coords.add((cell_x, cell_y))
                self.add_ship_from_cell(cell_x, cell_y, ship)

    def find_targets_in_range(self, ship):
        targets = []
        for x in range(max(0, ship.pos_x - ship.attack_range), min(self.width, ship.pos_x + ship.attack_range + 1)):
            for y in range(max(0, ship.pos_y - ship.attack_range), min(self.height, ship.pos_y + ship.attack_range + 1)):
                target = self.cells[x][y]
                if target and target.ship_type != ship.ship_type:
                    targets.append(target)
        return targets

    def find_ships_in_vision_range(self, ship):
        ships_in_range = []
        for x in range(max(0, ship.pos_x - ship.vision_range), min(self.width, ship.pos_x + ship.vision_range + 1)):
            for y in range(max(0, ship.pos_y - ship.vision_range), min(self.height, ship.pos_y + ship.vision_range + 1)):
                target = self.cells[x][y]
                if target and target != ship:
                    ships_in_range.append(target)
        return ships_in_range