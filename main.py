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



class Ship:
    def __init__(self, color):
        self.color = color

    def draw(self, x, y, screen, cell_size):
        pygame.draw.rect(screen, self.color, (x, y, cell_size, cell_size))


# Создание сетки и корабля
grid = Grid(grid_width, grid_height, grid_size)
ship = Ship(blue)
enemy_ship = Ship(red)


grid.add_ship_from_cell(1, 1, ship)

grid.add_ship_from_cell(2, 2, enemy_ship)


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

