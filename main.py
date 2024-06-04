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
flash_color = (255, 255, 0)  # Цвет мигания

# Настройки сетки
grid_size = 30
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

    def move_ship(self, ship, direction):
        if direction == "right" and grid_width - 1 > ship.pos_x:
            self.move_ship2position(ship, (ship.pos_x + 1, ship.pos_y))
        elif direction == "left" and 0 < ship.pos_x:
            self.move_ship2position(ship, (ship.pos_x - 1, ship.pos_y))
        elif direction == "up" and 0 < ship.pos_y:
            self.move_ship2position(ship, (ship.pos_x, ship.pos_y - 1))
        elif direction == "down" and grid_height - 1 > ship.pos_y:
            self.move_ship2position(ship, (ship.pos_x, ship.pos_y + 1))

    def move_ship_randomly(self, ship):
        directions = ship.get_available_directions(self)
        if directions:
            direction = random.choice(directions)
            self.move_ship(ship, direction)

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

class Ship:
    def __init__(self, color, speed=1, vision_range=3, attack_range=1, health=100, power=10, accuracy=0.7, attack_delay=30):
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
            self.color = flash_color if self.flash_timer % 2 == 0 else self.base_color
        else:
            self.color = self.base_color

    def calculate_strength(self, ships):
        strength = 0
        for ship in ships:
            strength += ship.health + ship.power
        return strength

    def get_available_directions(self, grid):
        directions = []
        if self.pos_x < grid_width - 1 and not grid.cells[self.pos_x + 1][self.pos_y]:
            directions.append("right")
        if self.pos_x > 0 and not grid.cells[self.pos_x - 1][self.pos_y]:
            directions.append("left")
        if self.pos_y > 0 and not grid.cells[self.pos_x][self.pos_y - 1]:
            directions.append("up")
        if self.pos_y < grid_height - 1 and not grid.cells[self.pos_x][self.pos_y + 1]:
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

class OurShip(Ship):
    def __init__(self, color=(0, 0, 255), speed=1, vision_range=7, attack_range=7, health=100, power=10, accuracy=0.7, attack_delay=30):
        super().__init__(color, speed, vision_range, attack_range, health, power, accuracy, attack_delay)
        self.ship_type = "our"

class EnemyShip(Ship):
    def __init__(self, color=(255, 0, 0), speed=1, vision_range=7, attack_range=7, health=100, power=10, accuracy=0.7, attack_delay=30):
        super().__init__(color, speed, vision_range, attack_range, health, power, accuracy, attack_delay)
        self.ship_type = "enemy"

# Создание сетки и кораблей
grid = Grid(grid_width, grid_height, grid_size)

# enemy_ship1 = EnemyShip(speed=40, attack_delay=10)
# enemy_ship2 = EnemyShip(speed=40, attack_delay=10)
#
# grid.add_ship_from_cell(0, 0, enemy_ship1)
# grid.add_ship_from_cell(1, 0, enemy_ship2)
#
# our_ship1 = OurShip(speed=40, attack_delay=10)
# our_ship2 = OurShip(speed=40, attack_delay=10)
#
# grid.add_ship_from_cell(0, 10, our_ship1)
# grid.add_ship_from_cell(1, 10, our_ship2)

def add_ship2game(ship, x, y, ships):
    grid.add_ship_from_cell(x, y, ship)
    ships.append(ship)

ships = []
add_ship2game(EnemyShip(speed=40, attack_delay=10), 10, 0, ships)
add_ship2game(EnemyShip(speed=40, attack_delay=10), 1, 0, ships)



add_ship2game(OurShip(speed=40, attack_delay=10), 0, 12, ships)
add_ship2game(OurShip(speed=40, attack_delay=10), 10, 12, ships)

clock = pygame.time.Clock()
FPS = 10

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
        if ship.move_timer >= 60:
            direction = None
            ships_in_range = grid.find_ships_in_vision_range(ship)
            if ships_in_range:
                for target in ships_in_range:
                    if target.ship_type != ship.ship_type and ship.should_move_towards(target):
                        direction = ship.choose_direction_based_on_vision(grid)
                        break
            if direction:
                grid.move_ship(ship, direction)
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
