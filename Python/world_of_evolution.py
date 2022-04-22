import copy
import random
import re

import pygame  # pip install pygame

# Моделирование жизни клетки
WORLD_SIZE = [64, 64]  # Размер мира x y
CELL_SIZE = 14  # Размер ячейки мира при отрисовке в пикселях
SPAWN_CELLS = 256  # Сколько появится в мире
CELLS_COLORS = (  # RGB цвета, которые может иметь клетка
    (200, 0, 0),
    (0, 200, 0),
    (0, 0, 200),
    (200, 200, 0),
    (200, 0, 200),
    (0, 200, 200),
    (160, 120, 80),
    (80, 120, 160)
)
GENS_LEN = 4  # Количество генов действия в геноме клетки
START_ENERGY = 250  # Со скольки энергии клетка
ENERGY_TO_MULTIPLY = 3000  # Не используется
FOOD_ENERGY = 30  # Сколько энергии даёт еда
BITE_ENERGY = 30  # Сколько энергии забирает атака
FOOD_AMOUNT = 120  # Сколько едениц еды заспавнится с самого начала
FOOD_SPAWN_RATE = 2  # Сколько едениц еды в фрейм будет спавнится
MEAT_AMOUNT = 60  # Сколько едениц мяса заспавнится с самого начала
MEAT_ENERGY = 50 # Сколько энергии даёт мясо
# Сколько едениц стен в мире (не считая стен по периметру мира)
WALL_AMOUNT = 60
FRAMES_PES_SEC = 8  # Сколько фреймов моделирования будет проходить в секунду


class Food():
    # Растительная пища, которую клетки будут есть
    def __init__(self, energy):
        self.__energy = energy  # Сколько энергии даст клетке еда, если будет сьедена

    def get_energy(self):
        return self.__energy


class Meat():
    # Пища, которая раньше была клеткой
    def __init__(self, energy):
        self.__energy = energy  # Сколько энергии даст клетке еда, если будет сьедена

    def get_energy(self):
        return self.__energy


class Wall():
    pass  # Ты ничего не сделаешь со стеной


class Cell():
    # Он хочет жить.
    def __init__(self, gens, rotation, energy=START_ENERGY) -> None:
        self.__energy = energy  # текущая энергия клетки
        self.__age = 0  # текущий возраст клетки
        # куда смотрит клетка (формула значение*45 градусов)
        self.__rotation = rotation
        self.__pain = False  # Испытывает боль от чужой атаки
        self.__food_eaten = 0  # сколько еды клетка сьела за свою жизнь
        self.__kills = 0  # сколько убийств сделала клетка за свою жизнь
        self.__bites = 0  # сколько раз клетка укусила своих сородичей за свою жизнь
        self.__kids = 0  # сколько детей имеет эта клетка
        self.__gen = 0  # Какой ген генома сейчас активен
        self.__gens = gens

    def get_stats(self) -> dict:
        return {"id": self.__gens['id'],
                "energy": self.__energy,
                "max_energy": self.__gens['energy_to_multiply'],
                "age": self.__age,
                "max_age": self.__gens['max_age'],
                "food": self.__food_eaten,
                "bites": self.__bites,
                "kills": self.__kills,
                "kids": self.__kids,
                "mutate_chance": self.__gens['mutate_chance']}

    def get_pain_gen(self) -> str:
        return f"{self.__gens['pain_gen']['none']}{self.__gens['pain_gen']['food']}{self.__gens['pain_gen']['meat']}{self.__gens['pain_gen']['cell_same_color']}{self.__gens['pain_gen']['cell_different_color']}{self.__gens['pain_gen']['wall']}{self.__gens['pain_gen']['unable_to_attack']}"

    def get_gen(self, gen_id) -> str:
        return f"{self.__gens['gens'][gen_id]['none']}{self.__gens['gens'][gen_id]['food']}{self.__gens['gens'][gen_id]['meat']}{self.__gens['gens'][gen_id]['cell_same_color']}{self.__gens['gens'][gen_id]['cell_different_color']}{self.__gens['gens'][gen_id]['wall']}{self.__gens['gens'][gen_id]['unable_to_attack']}"

    def get_color(self) -> tuple:
        return CELLS_COLORS[self.__gens['color']]

    def eye_positon(self, x, y) -> tuple:
        positons = (
            (x+4, y+(CELL_SIZE/2)),
            (draw_x+4, draw_y+4),
            (draw_x+(CELL_SIZE/2), draw_y+4),
            (draw_x+(CELL_SIZE-4), draw_y+4),
            (draw_x+(CELL_SIZE-4), draw_y+(CELL_SIZE/2)),
            (draw_x+(CELL_SIZE-4), draw_y+(CELL_SIZE-4)),
            (draw_x+(CELL_SIZE/2), draw_y+(CELL_SIZE-4)),
            (draw_x+4, draw_y+(CELL_SIZE-4)))
        return positons[self.__rotation]

    def bited(self):
        self.__energy -= BITE_ENERGY
        self.__pain = True

    def look(self, x, y) -> list:
        if self.__rotation == 7 or 0 <= self.__rotation <= 1:
            rx = x - 1
        elif 3 <= self.__rotation <= 5:
            rx = x + 1
        else:
            rx = x + 0
        if 1 <= self.__rotation <= 3:
            ry = y - 1
        elif 5 <= self.__rotation <= 7:
            ry = y + 1
        else:
            ry = y + 0
        return [rx, ry]

    def multiply(self, x, y, lc) -> None:
        global bot_id
        global world
        global cursor_pos
        world[x][y], world[lc[0]][lc[1]] = world[lc[0]][lc[1]], world[x][y]  # пройти вперёд
        self.__kids += 1
        if cursor_pos == [x, y]:
            cursor_pos = lc
        gens = copy.deepcopy(self.__gens)
        self.__energy = int(self.__energy/2)
        if random.randint(0, 100) <= self.__gens['mutate_chance']:
            to_mutate = random.randint(0, 6)
            if to_mutate == 0:
                gens["color"] = random.randint(0, len(CELLS_COLORS)-1)
            elif to_mutate == 1:
                gens["to_attack_cell"] = random.randint(-100, 100)
            elif to_mutate == 2:
                gens["max_age"] = random.randint(1000, 15000)
            elif to_mutate == 3:
                gens["energy_to_multiply"] = random.randint(500, 2500)
            elif to_mutate == 4:
                gens["mutate_chance"] = random.randint(1, 100)
            elif to_mutate == 5:
                gens["pain_gen"] = {"none": random.randint(0, 3), "food": random.randint(0, 3), "meat": random.randint(0, 3), "cell_same_color": random.randint(
                    0, 3), "cell_different_color": random.randint(0, 3), "wall": random.randint(0, 3), "unable_to_attack": random.randint(0, 2)}
            elif to_mutate == 6:
                gens["gens"][random.randint(0, GENS_LEN-1)] = {"none": random.randint(0, 3), "food": random.randint(0, 3), "meat": random.randint(
                    0, 3), "cell_same_color": random.randint(0, 3), "cell_different_color": random.randint(0, 3), "wall": random.randint(0, 3), "unable_to_attack": random.randint(0, 2)}
        gens['id'] = bot_id
        world[x][y] = Cell(gens, random.randint(0, 7), self.__energy)
        bot_id += 1

    def brains(self, x, y, gen, lc) -> None:
        global cursor_pos
        global world
        if world[lc[0]][lc[1]] == 0:
            execute = gen["none"]
        elif isinstance(world[lc[0]][lc[1]], Wall):
            execute = gen["wall"]
        elif isinstance(world[lc[0]][lc[1]], Food):
            execute = gen["food"]
        elif isinstance(world[lc[0]][lc[1]], Meat):
            execute = gen["meat"]
        elif isinstance(world[lc[0]][lc[1]], Cell):
            if self.get_color() == world[lc[0]][lc[1]].get_color():
                execute = gen["cell_same_color"]
            else:
                execute = gen["cell_different_color"]
        if execute == 1:
            self.__energy -= 1
            self.__rotation -= 1
            self.__rotation %= 8
        elif execute == 2:
            self.__energy -= 1
            self.__rotation += 1
            self.__rotation %= 8
        elif execute == 3:
            if world[lc[0]][lc[1]] == 0:
                self.__energy -= 1
                world[x][y], world[lc[0]][lc[1]] = world[lc[0]][lc[1]], world[x][y]
                if cursor_pos == [x, y]:
                    cursor_pos = lc
            elif isinstance(world[lc[0]][lc[1]], Food):
                self.__energy += world[lc[0]][lc[1]].get_energy()
                self.__food_eaten += 1
                world[lc[0]][lc[1]] = 0
            elif isinstance(world[lc[0]][lc[1]], Meat):
                self.__energy += world[lc[0]][lc[1]].get_energy()
                self.__food_eaten += 1
                world[lc[0]][lc[1]] = 0
            elif isinstance(world[lc[0]][lc[1]], Cell):
                if self.__energy > world[lc[0]][lc[1]].get_stats()['energy'] + self.__gens['to_attack_cell']:
                    self.__energy -= 1
                    self.__bites += 1
                    world[lc[0]][lc[1]].bited()
                    if world[lc[0]][lc[1]].get_stats()['energy'] <= 0:
                        self.__kills += 1
                else:
                    execute = gen["unable_to_attack"]
                    if execute == 1:
                        self.__energy -= 1
                        self.__rotation -= 1
                        self.__rotation %= 8
                    elif execute == 2:
                        self.__energy -= 1
                        self.__rotation += 1
                        self.__rotation %= 8

    def do(self, x, y) -> None:
        global world
        # Если у клетки нет энергии или она слишком старая
        if self.__energy <= 0 or self.__age >= self.__gens['max_age']:
            log[self.__gens['id']] = copy.deepcopy(self)  # Помянем
            world[x][y] = Meat(MEAT_ENERGY)  # И заменим мясом
            return
        lc = self.look(x, y)  # Определяем на какую ячейку клетка смотрит
        # Если может делится и впереди свободное место
        if self.__energy >= self.__gens['energy_to_multiply'] and world[lc[0]][lc[1]] == 0:
            self.multiply(x, y, lc)  # Делится
            return
        if self.__pain: # Если больно
            self.brains(x, y, self.__gens['pain_gen'], lc) # Делает то, что должна делать от боли
            self.__pain = False # Боль длится ровно одну итерацию
        else: # Если всё ок
            self.brains(x, y, self.__gens['gens'][self.__gen], lc) # Делает то, что предписано геном
            self.__gen += 1 # В следующий раз сработает другой ген
            self.__gen %= GENS_LEN # Зациклено
        self.__age += 1 # Клетка стареет
        

def spawn_gens():
    global bot_id
    gens = {"id": bot_id,  # Каждая клетка пронумерована
            # Всего у ботов будет 8 цветов (от 0 до 7)
            "color": random.randint(0, len(CELLS_COLORS)-1),
            # Условия для атаки клетки (какая разница в энергии клеток должна быть)
            "to_attack_cell": random.randint(-100, 100),
            # возраст, после которого клетка умрёт
            "max_age": random.randint(1000, 15000),
            # cколько энергии клетка должна иметь, чтобы размножится
            "energy_to_multiply": random.randint(500, 2500),
            # шанс мутации клетки (от 0 до 100)
            "mutate_chance": random.randint(1, 100),
            # дальше идут гены действия
            # 0: Ничего
            # 1: Повернутся влево
            # 2: Повернутся вправо
            # 3: Спецефическое действие для чего-то впереди (есть, атаковать или идти вперёд)
            "pain_gen": {
                "none": random.randint(0, 3),
                "food": random.randint(0, 3),
                "meat": random.randint(0, 3),
                "cell_same_color": random.randint(0, 3),
                "cell_different_color": random.randint(0, 3),
                "wall": random.randint(0, 3),
                "unable_to_attack": random.randint(0, 2)},
            "gens": [{
                "none": random.randint(0, 3),
                "food": random.randint(0, 3),
                "meat": random.randint(0, 3),
                "cell_same_color": random.randint(0, 3),
                "cell_different_color": random.randint(0, 3),
                "wall": random.randint(0, 3),
                "unable_to_attack": random.randint(0, 2)}for _ in range(GENS_LEN)
            ]
            }
    bot_id += 1
    return gens

world = [[0 for _ in range(WORLD_SIZE[1])] for _ in range(WORLD_SIZE[0])]
for xi, x in enumerate(world):
    for yi, y in enumerate(x):
        if xi == 0 or yi == 0 or xi == WORLD_SIZE[0]-1 or yi == WORLD_SIZE[1]-1:
            world[xi][yi] = Wall()

log = {}  # Сюда будем записывать ботов после их смерти
# Помещаем в мир еду
for _ in range(FOOD_AMOUNT):
    coords = [random.randint(1, WORLD_SIZE[0]-2),
              random.randint(1, WORLD_SIZE[1]-2)]
    if world[coords[0]][coords[1]] == 0:
        world[coords[0]][coords[1]] = Food(FOOD_ENERGY)
# Помещаем в мир мясо
for _ in range(MEAT_AMOUNT):
    coords = [random.randint(1, WORLD_SIZE[0]-2),
              random.randint(1, WORLD_SIZE[1]-2)]
    if world[coords[0]][coords[1]] == 0:
        world[coords[0]][coords[1]] = Meat(MEAT_ENERGY)
# Помещаем в мир рандомные стены
for _ in range(WALL_AMOUNT):
    coords = [random.randint(1, WORLD_SIZE[0]-2),
              random.randint(1, WORLD_SIZE[1]-2)]
    if world[coords[0]][coords[1]] == 0:
        world[coords[0]][coords[1]] = Wall()
# И, наконец, создаём ботов с рандомным интеллектом
bot_id = 0
for _ in range(SPAWN_CELLS):
    coords = [random.randint(1, WORLD_SIZE[0]-2),
              random.randint(1, WORLD_SIZE[1]-2)]
    if world[coords[0]][coords[1]] == 0:
        world[coords[0]][coords[1]] = Cell(spawn_gens(), random.randint(0, 7))
ON = True  # Задел на бесконечный цикл
pygame.init()  # Инициализируем pygame
pygame.font.init()  # Инициализируем модуль шрифтов pygame
# Подгоняем окно pygame под размер мира
win = pygame.display.set_mode(
    (250+CELL_SIZE*WORLD_SIZE[0], 25+CELL_SIZE*WORLD_SIZE[1]))
clock = pygame.time.Clock()  # CLOCK?mclock⏰⏰⏰⏰⏰⏰⏰⏰⏰⌚⏰⌚⏰⌚⏰⌚
font = pygame.font.Font(pygame.font.match_font("Monospace"), 15)  # Выбор шрифта
pygame.display.set_caption("Симуляция жизни")  # Заголовок окна
simulate = True
iterations = 0  # Отслеживаем количество итераций в поколении
draw_mode = 0  # 0 - рисуем мир, 1 - не рисуем мир
food_to_spawn = 0
cursor_pos = [1, 1]
while ON:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            ON = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                if 0 <= int((event.pos[0] - 5)/CELL_SIZE) <= WORLD_SIZE[0] and 0 <= int((event.pos[1] - 5)/CELL_SIZE) <= WORLD_SIZE[1]:
                    cursor_pos = [int((event.pos[0] - 5)/CELL_SIZE), int((event.pos[1] - 5)/CELL_SIZE)]
                else:
                    draw_mode += 1
                    draw_mode %= 2
    win.fill((25, 25, 25))
    draw_x = 5
    draw_y = 5
    food = 0
    meat = 0
    cell = 0
    for x in world:
        for y in x:
            if y == 0:
                pygame.draw.rect(
                    win, (0, 0, 0), (draw_x+1, draw_y+1, CELL_SIZE-2, CELL_SIZE-2))
            elif isinstance(y, Food):
                pygame.draw.rect(win, (0, 255, 0), (draw_x+1, draw_y+1, CELL_SIZE-2, CELL_SIZE-2))
                food += 1
            elif isinstance(y, Meat):
                pygame.draw.rect(win, (255, 0, 0), (draw_x+1, draw_y+1, CELL_SIZE-2, CELL_SIZE-2))
                meat += 1
            elif isinstance(y, Wall):
                pygame.draw.rect(win, (255, 255, 255), (draw_x+1, draw_y+1, CELL_SIZE-2, CELL_SIZE-2))
            elif isinstance(y, Cell):
                pygame.draw.rect(win, y.get_color(), (draw_x+1, draw_y+1, CELL_SIZE-2, CELL_SIZE-2))
                pygame.draw.circle(win, (0, 0, 0), y.eye_positon(draw_x, draw_y), 2)
                cell += 1
            pygame.draw.rect(win, (255, 255, 255), (5+cursor_pos[0]*CELL_SIZE, 5+cursor_pos[1]*CELL_SIZE, CELL_SIZE, CELL_SIZE), 2)
            draw_y += CELL_SIZE
        draw_x += CELL_SIZE
        draw_y = 5
    win.blit(font.render(f"Итерация: {iterations}; Клеток/Еды/Трупов: {cell}/{food}/{meat}", 1, (255, 255, 255)), (5, CELL_SIZE*WORLD_SIZE[1]+5))
    if world[cursor_pos[0]][cursor_pos[1]] == 0:
        win.blit(font.render("Ничего", 1, (255, 255, 255)), (CELL_SIZE*WORLD_SIZE[0]+10, 5))
        win.blit(font.render(f"Координаты: {cursor_pos}", 1, (255, 255, 255)), (CELL_SIZE*WORLD_SIZE[0]+10, 20))
    if isinstance(world[cursor_pos[0]][cursor_pos[1]], Wall):
        win.blit(font.render("Cтена", 1, (255, 255, 255)), (CELL_SIZE*WORLD_SIZE[0]+10, 5))
        win.blit(font.render(f"Координаты: {cursor_pos}", 1, (255, 255, 255)), (CELL_SIZE*WORLD_SIZE[0]+10, 20))
    if isinstance(world[cursor_pos[0]][cursor_pos[1]], Food):
        win.blit(font.render("Растительная еда", 1, (255, 255, 255)), (CELL_SIZE*WORLD_SIZE[0]+10, 5))
        win.blit(font.render(f"Координаты: {cursor_pos}", 1, (255, 255, 255)), (CELL_SIZE*WORLD_SIZE[0]+10, 20))
        win.blit(font.render(f"Энегрия: {world[cursor_pos[0]][cursor_pos[1]].get_energy()}", 1, (255, 255, 255)), (CELL_SIZE*WORLD_SIZE[0]+10, 35))
    if isinstance(world[cursor_pos[0]][cursor_pos[1]], Meat):
        win.blit(font.render("Мясо (труп клетки)", 1, (255, 255, 255)), (CELL_SIZE*WORLD_SIZE[0]+10, 5))
        win.blit(font.render(f"Координаты: {cursor_pos}", 1, (255, 255, 255)), (CELL_SIZE*WORLD_SIZE[0]+10, 20))
        win.blit(font.render(f"Энегрия: {world[cursor_pos[0]][cursor_pos[1]].get_energy()}", 1, (255, 255, 255)), (CELL_SIZE*WORLD_SIZE[0]+10, 35))
    if isinstance(world[cursor_pos[0]][cursor_pos[1]], Cell):
        cell_stats = world[cursor_pos[0]][cursor_pos[1]].get_stats()
        win.blit(font.render(f"Клетка №{cell_stats['id']}", 1, (255, 255, 255)), (CELL_SIZE*WORLD_SIZE[0]+10, 5))
        win.blit(font.render(f"Координаты: {cursor_pos}", 1, (255, 255, 255)), (CELL_SIZE*WORLD_SIZE[0]+10, 20))
        win.blit(font.render(f"Энегрия:    {cell_stats['energy']}/{cell_stats['max_energy']}", 1, (255, 255, 255)), (CELL_SIZE*WORLD_SIZE[0]+10, 35))
        win.blit(font.render(f"Возраст:    {cell_stats['age']}/{cell_stats['max_age']}", 1, (255, 255, 255)), (CELL_SIZE*WORLD_SIZE[0]+10, 50))
        win.blit(font.render(f"Cъел еды:   {cell_stats['food']}", 1, (255, 255, 255)), (CELL_SIZE*WORLD_SIZE[0]+10, 65))
        win.blit(font.render(f"Атак:       {cell_stats['bites']}", 1, (255, 255, 255)), (CELL_SIZE*WORLD_SIZE[0]+10, 80))
        win.blit(font.render(f"Убийств:    {cell_stats['kills']}", 1, (255, 255, 255)), (CELL_SIZE*WORLD_SIZE[0]+10, 95))
        win.blit(font.render(f"Детей:      {cell_stats['kids']}", 1, (255, 255, 255)), (CELL_SIZE*WORLD_SIZE[0]+10, 110))
        win.blit(font.render("Геном NFMSDWU", 1, (255, 255, 255)),(CELL_SIZE*WORLD_SIZE[0]+10, 125))
        win.blit(font.render(f"Боль: {world[cursor_pos[0]][cursor_pos[1]].get_pain_gen()}", 1, (255, 255, 255)), (CELL_SIZE*WORLD_SIZE[0]+10, 140))
        draw_x = 155
        for i in range(GENS_LEN):
            win.blit(font.render(f"№ {i:02d}: {world[cursor_pos[0]][cursor_pos[1]].get_gen(i)}", 1, (255, 255, 255)), (CELL_SIZE*WORLD_SIZE[0]+10, draw_x))
            draw_x += 15
        win.blit(font.render(f"Шанс на мутацию: {cell_stats['mutate_chance']}%", 1, (255, 255, 255)), (CELL_SIZE*WORLD_SIZE[0]+10, draw_x))
    pygame.display.update()
    if simulate and draw_mode == 0:  # Исполняем код каждой клетки:
        # Копируем мир, чтобы мир не менялся для кода во время итерации
        cworld = copy.deepcopy(world)
        for xi, x in enumerate(cworld):  # Ищем клетки в копии мира
            for yi, y in enumerate(x):
                if isinstance(y, Cell):  # Если находим клетку
                    y = world[xi][yi]  # Берем её не из копии мира
                    y.do(xi, yi)  # И исполняем её код
        iterations += 1
        food_to_spawn += FOOD_SPAWN_RATE
        for _ in range(int(food_to_spawn)):  # Спавним новую растительную еду
            coords = [random.randint(1, WORLD_SIZE[0]-2),
                      random.randint(1, WORLD_SIZE[1]-2)]
            if world[coords[0]][coords[1]] == 0:
                world[coords[0]][coords[1]] = Food(FOOD_ENERGY)
        food_to_spawn -= int(food_to_spawn)
        if cell == 0:
            simulate = False
    clock.tick(FRAMES_PES_SEC)
pygame.quit()
