import random
import pygame
import sys
from grid import Grid
from ships import OurShip, EnemyShip
from config import config


pygame.init()

# Настройки окна
screen_width, screen_height = config["screen_width"], config["screen_height"]
screen = pygame.display.set_mode((screen_width, screen_height))

# Цвета
background_color = config["background_color"]
grid_color = config["grid_color"]
flash_color = config["flash_color"]  # Цвет мигания

# Настройки сетки
grid_size = config["grid_size"]
grid_width = screen_width // grid_size
grid_height = screen_height // grid_size


# Создание сетки и кораблей
grid = Grid(grid_width, grid_height, grid_size, grid_color=grid_color)



def add_ship2game(ship, x, y, ships):
    grid.add_ship_from_cell(x, y, ship)
    ships.append(ship)

ships = []
add_ship2game(EnemyShip(speed=40, attack_delay=10), 10, 0, ships)
add_ship2game(EnemyShip(speed=40, attack_delay=10), 1, 0, ships)
add_ship2game(EnemyShip(speed=40, attack_delay=10), 4, 0, ships)
add_ship2game(EnemyShip(speed=40, attack_delay=10), 6, 0, ships)
add_ship2game(EnemyShip(speed=40, attack_delay=10), 8, 0, ships)
add_ship2game(EnemyShip(speed=40, attack_delay=10), 12, 0, ships)



add_ship2game(OurShip(speed=40, attack_delay=10), 0, 12, ships)
add_ship2game(OurShip(speed=40, attack_delay=10), 12, 12, ships)
add_ship2game(OurShip(speed=40, attack_delay=10), 3, 12, ships)
add_ship2game(OurShip(speed=40, attack_delay=10), 5, 12, ships)
add_ship2game(OurShip(speed=40, attack_delay=10), 7, 12, ships)
add_ship2game(OurShip(speed=40, attack_delay=10), 10, 12, ships)

clock = pygame.time.Clock()
FPS = config["FPS"]
action_threshold = config["action_threshold"]

# Основной цикл игры
while True:
    clock.tick(FPS)

    # Список для удаления уничтоженных кораблей
    ships_to_remove = []

    # Обновляем таймеры и перемещаем корабли
    for ship in ships:
        ship.move_timer += ship.speed
        ship.attack_timer += 1

        # Перемещение
        if ship.move_timer >= action_threshold:
            direction = None
            ships_in_range = grid.find_ships_in_vision_range(ship)
            if ships_in_range:
                for target in ships_in_range:
                    if target.ship_type != ship.ship_type and ship.should_move_towards(target):
                        direction = ship.choose_direction_based_on_vision(grid)
                        break
            if direction:
                if direction == ship.direction:
                    grid.move_ship(ship)
                else:
                    grid.rotate_ship2direction(ship, direction)
            else:
                grid.move_ship_randomly(ship)
            ship.move_timer = 0

        # Атака
        if ship.attack_timer >= ship.attack_delay:
            targets = grid.find_targets_in_range(ship)
            if targets:
                target = random.choice(targets)  # Выбираем случайную цель для атаки
                if ship.attack(target):
                    ships_to_remove.append(target)
            ship.attack_timer = 0

        # Обновление состояния корабля (мигание и т.д.)
        ship.update()

    # Удаление уничтоженных кораблей из сетки и списка активных кораблей
    for ship in ships_to_remove:
        grid.delete_ship(ship.pos_x, ship.pos_y)
        if ship in ships:
            ships.remove(ship)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        # if event.type == pygame.MOUSEBUTTONDOWN:
        #     mouseX, mouseY = pygame.mouse.get_pos()
        #     grid.add_ship_from_coords(mouseX, mouseY, ship)

    screen.fill(background_color)
    grid.draw(screen)
    # Отрисовываем корабли на поле
    for x in range(grid.width):
        for y in range(grid.height):
            if grid.cells[x][y] is not None:
                ship_x = x * grid.cell_size
                ship_y = y * grid.cell_size
                grid.cells[x][y].draw(ship_x, ship_y, screen, grid.cell_size)

    pygame.display.flip()
