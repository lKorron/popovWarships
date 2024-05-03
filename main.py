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
grid_size = 15
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
            ship.pos_x = grid_x
            ship.pos_y = grid_y

    def add_ship_from_cell(self, cell_x, cell_y, ship):
        if self.cells[cell_x][cell_y] is None:  # Проверяем, свободна ли ячейка
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


    def move_ship(self, ship, direction):
        if direction == "right":
            if grid_width - 1 > ship.pos_x:
                self.move_ship2position(ship, (ship.pos_x + 1, ship.pos_y))

        elif direction == "left":
            if 0 < ship.pos_x:
                self.move_ship2position(ship, (ship.pos_x - 1, ship.pos_y))

        elif direction == "up":
            if 0 < ship.pos_y:
                self.move_ship2position(ship, (ship.pos_x, ship.pos_y - 1))

        elif direction == "down":
            if grid_height - 1 > ship.pos_y:
                self.move_ship2position(ship, (ship.pos_x, ship.pos_y + 1))

    def move_ship_randomly(self, ship):
        direction = random.randint(1, 4)
        if direction == 1:
            self.move_ship(ship, "right")
        elif direction == 2:
            self.move_ship(ship, "left")
        elif direction == 3:
            self.move_ship(ship, "up")
        elif direction == 4:
            self.move_ship(ship, "down")



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
        self.pos_x = None
        self.pos_y = None
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


enemy_ship1 = EnemyShip()
enemy_ship2 = EnemyShip()

grid.add_ship_from_cell(0, 0, enemy_ship1)
grid.add_ship_from_cell(1, 0, enemy_ship2)

our_ship1 = OurShip()
our_ship2 = OurShip()


grid.add_ship_from_cell(0, 30, our_ship1)
grid.add_ship_from_cell(1, 30, our_ship2)







# grid.spawn_ships(enemy_ship, ships_count=6)


# grid.add_ship_from_cell(1, 1, ship)
#
# grid.add_ship_from_cell(2, 2, enemy_ship)
clock = pygame.time.Clock()
FPS = 10

# Основной цикл игры
while True:
    clock.tick(FPS)
    grid.move_ship_randomly(enemy_ship1)
    grid.move_ship_randomly(enemy_ship2)

    grid.move_ship_randomly(our_ship1)
    grid.move_ship_randomly(our_ship2)



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

