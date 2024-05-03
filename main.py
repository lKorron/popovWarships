import random

import pygame
import sys

pygame.init()

# Настройки окна
screen_width, screen_height = 800, 600
screen = pygame.display.set_mode((screen_width, screen_height))

# Цвета
black = (0, 0, 0)
white = (255, 255, 255)
blue = (0, 0, 255)
red = (255, 0, 0)

# Настройки сетки
grid_size = 50
grid_width = screen_width // grid_size
grid_height = screen_height // grid_size


class Grid:
    def __init__(self, width, height, cell_size):
        self.width = width
        self.height = height
        self.cell_size = cell_size
        self.cells = [[None for _ in range(height)] for _ in range(width)]

    def draw(self, screen):
        for x in range(0, self.width * self.cell_size, self.cell_size):
            for y in range(0, self.height * self.cell_size, self.cell_size):
                rect = pygame.Rect(x, y, self.cell_size, self.cell_size)
                pygame.draw.rect(screen, white, rect, 1)

    def add_ship_from_coords(self, x, y, ship):
        grid_x = x // self.cell_size
        grid_y = y // self.cell_size
        if self.cells[grid_x][grid_y] is None:  # Проверяем, свободна ли ячейка
            self.cells[grid_x][grid_y] = ship

    def add_ship_from_cell(self, cell_x, cell_y, ship):

        if self.cells[cell_x][cell_y] is None:  # Проверяем, свободна ли ячейка
            self.cells[cell_x][cell_y] = ship


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





class Ship:
    def __init__(self, color):
        self.color = color

    def draw(self, x, y, screen, cell_size):
        pygame.draw.rect(screen, self.color, (x, y, cell_size, cell_size))

class OurShip(Ship):
    def __init__(self, color=(0, 0, 255)):
        super().__init__(color)
        self.ship_type = "our"


class EnemyShip(Ship):
    def __init__(self, color=(255, 0, 0)):
        super().__init__(color)
        self.ship_type = "enemy"


# Создание сетки и корабля
grid = Grid(grid_width, grid_height, grid_size)


ship = Ship(blue)

our_ship = OurShip()
enemy_ship = EnemyShip()


grid.spawn_ships(our_ship, ships_count=6)
grid.spawn_ships(enemy_ship, ships_count=6)


# grid.add_ship_from_cell(1, 1, ship)
#
# grid.add_ship_from_cell(2, 2, enemy_ship)


# Основной цикл игры
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouseX, mouseY = pygame.mouse.get_pos()
            grid.add_ship_from_coords(mouseX, mouseY, ship)

    screen.fill(black)
    grid.draw(screen)
    # Отрисовываем корабли на поле
    for x in range(grid.width):
        for y in range(grid.height):
            if grid.cells[x][y] is not None:
                ship_x = x * grid.cell_size
                ship_y = y * grid.cell_size
                grid.cells[x][y].draw(ship_x, ship_y, screen, grid.cell_size)

    pygame.display.flip()

