import re
import pygame # pip install pygame
import random
import copy

# Моделирование жизни клетки
WORLD_SIZE = [64, 64] # Размер мира x y
CELL_SIZE = 14 # Размер ячейки мира при отрисовке в пикселях
SPAWN_CELLS = 256 # Сколько появится в мире
GENS_LEN = 4 # Количество генов действия в геноме клетки
START_ENERGY = 250 # Со скольки энергии клетка
ENERGY_TO_MULTIPLY = 3000 # Сколько энергии клетка должна иметь, чтобы размножится
MUTATE_CHANCE = 20 # Шанс от 0 до 100 в процентах что потомство будет с мутацией
FOOD_ENERGY = 30 # Сколько энергии даёт еда
BITE_ENERGY = 30 # Сколько энергии забирает атака
FOOD_AMOUNT = 120 # Сколько едениц еды в заспавнится с самого начала
FOOD_SPAWN_RATE = 2 # Сколько едениц еды в фрейм будет спавнится
MEAT_AMOUNT = 60 # Сколько едениц мяса заспавнится с самого начала
MEAT_ENERGY = 50 # Сколько энергии даёт мясо (мясо от клеток будет иметь другой уровень энергии)
WALL_AMOUNT = 60 # Сколько едениц стен в мире (не считая стен по периметру мира)
FRAMES_PES_SEC = 8 # Сколько фреймов моделирования будет проходить в секунду

class Food():
    # Растительная пища, которую клетки будут есть
    def __init__(self, energy):
        self.energy = energy # Сколько энергии даст клетке еда, если будет сьедена

class Meat():
    # Пища, которая раньше была клеткой
    def __init__(self, energy):
        self.energy = energy # Сколько энергии даст клетке еда, если будет сьедена

class Wall():
    def __init__(self):
        self.wall = "wall" # Ты ничего не сделаешь со стеной

class Cell():
    # Он хочет жить.
    def __init__(self, gens, rotation, energy=START_ENERGY) -> None:
        self.energy = energy # текущая энергия клетки
        self.age = 0 # текущий возраст клетки
        self.rotation = rotation # куда смотрит клетка (формула self.direction*45 градусов)
        self.pain = False # Испытывает боль от чужой атаки
        self.food_eaten = 0 # сколько еды клетка сьела за свою жизнь
        self.kills = 0 # сколько убийств сделала клетка за свою жизнь
        self.bites = 0 # сколько раз клетка укусила своих сородичей за свою жизнь
        self.kids = 0 # сколько детей имеет эта клетка
        self.gen = 0 # Какой ген генома сейчас активен
        self.gens = gens
    
    def look(self, x, y):
        if self.rotation == 7 or 0 <= self.rotation <= 1:
            rx = x - 1
        elif 3 <= self.rotation <= 5:
            rx = x + 1
        else:
            rx = x + 0
        if 1 <= self.rotation <= 3:
            ry = y - 1
        elif 5 <= self.rotation <= 7:
            ry = y + 1
        else:
            ry = y + 0
        return [rx, ry]
    
    
world = [[0 for _ in range(WORLD_SIZE[1])] for _ in range(WORLD_SIZE[0])]
for xi, x in enumerate(world):
    for yi, y in enumerate(x):
        if xi == 0 or yi == 0 or xi == WORLD_SIZE[0]-1 or yi == WORLD_SIZE[1]-1:
            world[xi][yi] = Wall()

log = {} # Сюда будем записывать ботов после их смерти
# Помещаем в мир еду
for _ in range(FOOD_AMOUNT):
    coords = [random.randint(1, WORLD_SIZE[0]-2), random.randint(1, WORLD_SIZE[1]-2)]
    if world[coords[0]][coords[1]] == 0:
        world[coords[0]][coords[1]] = Food(FOOD_ENERGY)
# Помещаем в мир мясо
for _ in range(MEAT_AMOUNT):
    coords = [random.randint(1, WORLD_SIZE[0]-2), random.randint(1, WORLD_SIZE[1]-2)]
    if world[coords[0]][coords[1]] == 0:
        world[coords[0]][coords[1]] = Meat(MEAT_ENERGY)
# Помещаем в мир рандомные стены
for _ in range(WALL_AMOUNT):
    coords = [random.randint(1, WORLD_SIZE[0]-2), random.randint(1, WORLD_SIZE[1]-2)]
    if world[coords[0]][coords[1]] == 0:
        world[coords[0]][coords[1]] = Wall()
# И, наконец, создаём ботов с рандомным интеллектом
bot_id = 0
for _ in range(SPAWN_CELLS):
    coords = [random.randint(1, WORLD_SIZE[0]-2), random.randint(1, WORLD_SIZE[1]-2)]
    if world[coords[0]][coords[1]] == 0:
        world[coords[0]][coords[1]] = Cell({"id": bot_id, # Каждая клетка пронумерована
            "color": random.randint(0, 7), # Всего у ботов будет 8 цветов (от 0 до 7)
            "to_attack_cell": random.randint(-100, 100), # Условия для атаки клетки (какая разница в энергии клеток должна быть)
            "max_age": random.randint(1000, 15000), # возраст, после которого клетка умрёт
            "energy_to_multiply": random.randint(500, 2500), # cколько энергии клетка должна иметь, чтобы размножится
            "mutate_chance": random.randint(1, 100), # шанс мутации клетки (от 0 до 100)
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
            "gens":[{
                "none": random.randint(0, 3),
                "food": random.randint(0, 3),
                "meat": random.randint(0, 3),
                "cell_same_color": random.randint(0, 3),
                "cell_different_color": random.randint(0, 3),
                "wall": random.randint(0, 3),
                "unable_to_attack": random.randint(0, 2)}for _ in range(GENS_LEN)
                ] 
        }, random.randint(0, 7))
        bot_id += 1
ON = True
pygame.init() # Инициализируем pygame
pygame.font.init() # Инициализируем модуль шрифтов pygame
win = pygame.display.set_mode((250+CELL_SIZE*WORLD_SIZE[0], 25+CELL_SIZE*WORLD_SIZE[1])) # Подгоняем окно pygame под размер мира
clock = pygame.time.Clock() # CLOCK?mclock⏰⏰⏰⏰⏰⏰⏰⏰⏰⌚⏰⌚⏰⌚⏰⌚
font = pygame.font.Font(pygame.font.match_font("Monospace"), 15)
pygame.display.set_caption("Симуляция жизни") # Заголовок окна
simulate = True
iterations = 0 # Отслеживаем количество итераций в поколении
draw_mode = 0 # 0 - рисуем мир, 1 - рисуем информацию о предыдущем поколении
food_to_spawn = 0 
cursor_pos = [1, 1]
while ON:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            ON = False
        if event.type == pygame.MOUSEBUTTONDOWN: # ЛКМ - переключить draw_mode
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
                pygame.draw.rect(win, (0, 0, 0), (draw_x+1, draw_y+1, CELL_SIZE-2, CELL_SIZE-2))
            elif isinstance(y, Food):
                pygame.draw.rect(win, (0, 255, 0), (draw_x+1, draw_y+1, CELL_SIZE-2, CELL_SIZE-2))
                food += 1
            elif isinstance(y, Meat):
                pygame.draw.rect(win, (255, 0, 0), (draw_x+1, draw_y+1, CELL_SIZE-2, CELL_SIZE-2))
                meat += 1
            elif isinstance(y, Wall):
                pygame.draw.rect(win, (255, 255, 255), (draw_x+1, draw_y+1, CELL_SIZE-2, CELL_SIZE-2))
            elif isinstance(y, Cell):
                if y.gens['color'] == 0:
                    color = (200, 0, 0)
                elif y.gens['color'] == 1:
                    color = (0, 200, 0)
                elif y.gens['color'] == 2:
                    color = (0, 0, 200)
                elif y.gens['color'] == 3:
                    color = (200, 200, 0)
                elif y.gens['color'] == 4:
                    color = (200, 0, 200)
                elif y.gens['color'] == 5:
                    color = (0, 200, 200)
                elif y.gens['color'] == 6:
                    color = (160, 120, 80)
                elif y.gens['color'] == 7:
                    color = (80, 120, 160)
                pygame.draw.rect(win, color, (draw_x+1, draw_y+1, CELL_SIZE-2, CELL_SIZE-2))
                if y.rotation == 0:
                    pygame.draw.circle(win, (0, 0, 0), (draw_x+4, draw_y+(CELL_SIZE/2)), 2)
                elif y.rotation == 1:
                    pygame.draw.circle(win, (0, 0, 0), (draw_x+4, draw_y+4), 2)
                elif y.rotation == 2:
                    pygame.draw.circle(win, (0, 0, 0), (draw_x+(CELL_SIZE/2), draw_y+4), 2)
                elif y.rotation == 3:
                    pygame.draw.circle(win, (0, 0, 0), (draw_x+(CELL_SIZE-4), draw_y+4), 2)
                elif y.rotation == 4:
                    pygame.draw.circle(win, (0, 0, 0), (draw_x+(CELL_SIZE-4), draw_y+(CELL_SIZE/2)), 2) 
                elif y.rotation == 5:
                    pygame.draw.circle(win, (0, 0, 0), (draw_x+(CELL_SIZE-4), draw_y+(CELL_SIZE-4)), 2) 
                elif y.rotation == 6:
                    pygame.draw.circle(win, (0, 0, 0), (draw_x+(CELL_SIZE/2), draw_y+(CELL_SIZE-4)), 2) 
                elif y.rotation == 7:
                    pygame.draw.circle(win, (0, 0, 0), (draw_x+4, draw_y+(CELL_SIZE-4)), 2) 
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
        win.blit(font.render(f"Энегрия: {world[cursor_pos[0]][cursor_pos[1]].energy}", 1, (255, 255, 255)), (CELL_SIZE*WORLD_SIZE[0]+10, 35))
    if isinstance(world[cursor_pos[0]][cursor_pos[1]], Meat):
        win.blit(font.render("Мясо (труп клетки)", 1, (255, 255, 255)), (CELL_SIZE*WORLD_SIZE[0]+10, 5))
        win.blit(font.render(f"Координаты: {cursor_pos}", 1, (255, 255, 255)), (CELL_SIZE*WORLD_SIZE[0]+10, 20))
        win.blit(font.render(f"Энегрия: {world[cursor_pos[0]][cursor_pos[1]].energy}", 1, (255, 255, 255)), (CELL_SIZE*WORLD_SIZE[0]+10, 35))
    if isinstance(world[cursor_pos[0]][cursor_pos[1]], Cell):
        win.blit(font.render(f"Клетка №{world[cursor_pos[0]][cursor_pos[1]].gens['id']}", 1, (255, 255, 255)), (CELL_SIZE*WORLD_SIZE[0]+10, 5))
        win.blit(font.render(f"Координаты: {cursor_pos}", 1, (255, 255, 255)), (CELL_SIZE*WORLD_SIZE[0]+10, 20))
        win.blit(font.render(f"Энегрия:    {world[cursor_pos[0]][cursor_pos[1]].energy}/{world[cursor_pos[0]][cursor_pos[1]].gens['energy_to_multiply']}", 1, (255, 255, 255)), (CELL_SIZE*WORLD_SIZE[0]+10, 35))
        win.blit(font.render(f"Возраст:    {world[cursor_pos[0]][cursor_pos[1]].age}/{world[cursor_pos[0]][cursor_pos[1]].gens['max_age']}", 1, (255, 255, 255)), (CELL_SIZE*WORLD_SIZE[0]+10, 50))
        win.blit(font.render(f"Cъел еды:   {world[cursor_pos[0]][cursor_pos[1]].food_eaten}", 1, (255, 255, 255)), (CELL_SIZE*WORLD_SIZE[0]+10, 65))
        win.blit(font.render(f"Атак:       {world[cursor_pos[0]][cursor_pos[1]].bites}", 1, (255, 255, 255)), (CELL_SIZE*WORLD_SIZE[0]+10, 80))
        win.blit(font.render(f"Убийств:    {world[cursor_pos[0]][cursor_pos[1]].kills}", 1, (255, 255, 255)), (CELL_SIZE*WORLD_SIZE[0]+10, 95))
        win.blit(font.render(f"Детей:      {world[cursor_pos[0]][cursor_pos[1]].kids}", 1, (255, 255, 255)), (CELL_SIZE*WORLD_SIZE[0]+10, 110))
        win.blit(font.render("Геном NFMSDWU", 1, (255, 255, 255)), (CELL_SIZE*WORLD_SIZE[0]+10, 125))
        win.blit(font.render(f"Боль: {world[cursor_pos[0]][cursor_pos[1]].gens['pain_gen']['none']}{world[cursor_pos[0]][cursor_pos[1]].gens['pain_gen']['food']}{world[cursor_pos[0]][cursor_pos[1]].gens['pain_gen']['meat']}{world[cursor_pos[0]][cursor_pos[1]].gens['pain_gen']['cell_same_color']}{world[cursor_pos[0]][cursor_pos[1]].gens['pain_gen']['cell_different_color']}{world[cursor_pos[0]][cursor_pos[1]].gens['pain_gen']['wall']}{world[cursor_pos[0]][cursor_pos[1]].gens['pain_gen']['unable_to_attack']}", 1, (255, 255, 255)), (CELL_SIZE*WORLD_SIZE[0]+10, 140))
        draw_x = 155
        for i, x in enumerate(world[cursor_pos[0]][cursor_pos[1]].gens['gens']):
            win.blit(font.render(f"№{i:03d}: {x['none']}{x['food']}{x['meat']}{x['cell_same_color']}{x['cell_different_color']}{x['wall']}{x['unable_to_attack']}", 1, (255, 255, 255)), (CELL_SIZE*WORLD_SIZE[0]+10, draw_x))
            draw_x += 15
        win.blit(font.render(f"Шанс на мутацию: {world[cursor_pos[0]][cursor_pos[1]].gens['mutate_chance']}%", 1, (255, 255, 255)), (CELL_SIZE*WORLD_SIZE[0]+10, draw_x))
    pygame.display.update()
    if simulate and draw_mode == 0: # Описание симуляции мира:
        cworld = copy.deepcopy(world)
        for xi, x in enumerate(cworld):
            for yi, y in enumerate(x):
                if isinstance(y, Cell):
                    y = world[xi][yi]
                else:
                    continue
                if isinstance(y, Cell): # Если клетка
                    if y.energy <= 0 or y.age >= y.gens['max_age']: # Если у клетки нет энергии или она слишком старая
                        log[y.gens['id']] = copy.deepcopy(y) # Помянем
                        world[xi][yi] = Meat(MEAT_ENERGY) # И заменим мясом
                        continue
                    look_coords = y.look(xi, yi)
                    if y.energy >= y.gens['energy_to_multiply']:
                        if world[look_coords[0]][look_coords[1]] == 0:
                            world[xi][yi], world[look_coords[0]][look_coords[1]] = world[look_coords[0]][look_coords[1]], world[xi][yi]
                            y.kids += 1
                            if cursor_pos == [xi, yi]:
                                cursor_pos = look_coords
                            gens = copy.deepcopy(y.gens)
                            y.energy = int(y.energy/2)
                            if random.randint(0, 100) > y.gens['mutate_chance']:
                                gens['id'] = bot_id
                                world[xi][yi] = Cell(gens, random.randint(0, 7), y.energy)
                                bot_id += 1
                            else:
                                to_mutate = random.randint(0, 6)
                                if to_mutate == 0:
                                    gens["color"] = random.randint(0, 7)
                                elif to_mutate == 1:
                                    gens["to_attack_cell"] = random.randint(-100, 100)
                                elif to_mutate == 2:
                                    gens["max_age"] = random.randint(1000, 15000)
                                elif to_mutate == 3:
                                    gens["energy_to_multiply"] = random.randint(500, 2500)
                                elif to_mutate == 4:
                                    gens["mutate_chance"] = random.randint(1, 100)
                                elif to_mutate == 5:
                                    gens["pain_gen"] = {"none": random.randint(0, 3), "food": random.randint(0, 3), "meat": random.randint(0, 3), "cell_same_color": random.randint(0, 3), "cell_different_color": random.randint(0, 3), "wall": random.randint(0, 3), "unable_to_attack": random.randint(0, 2)}
                                elif to_mutate == 6:
                                    gens["gens"][random.randint(0, GENS_LEN-1)] = {"none": random.randint(0, 3), "food": random.randint(0, 3), "meat": random.randint(0, 3), "cell_same_color": random.randint(0, 3), "cell_different_color": random.randint(0, 3), "wall": random.randint(0, 3), "unable_to_attack": random.randint(0, 2)}
                                gens['id'] = bot_id
                                world[xi][yi] = Cell(gens, random.randint(0, 7), y.energy)
                                bot_id += 1
                    if y.pain:
                        if world[look_coords[0]][look_coords[1]] == 0:
                            execute = y.gens['pain_gen']["none"]
                        elif isinstance(world[look_coords[0]][look_coords[1]], Wall):
                            execute = y.gens['pain_gen']["wall"]
                        elif isinstance(world[look_coords[0]][look_coords[1]], Food):
                            execute = y.gens['pain_gen']["food"]
                        elif isinstance(world[look_coords[0]][look_coords[1]], Meat):
                            execute = y.gens['pain_gen']["meat"]
                        elif isinstance(world[look_coords[0]][look_coords[1]], Cell):
                            if y.gens['color'] == world[look_coords[0]][look_coords[1]].gens['color']:
                                execute = y.gens['pain_gen']["cell_same_color"]
                            else:
                                execute = y.gens['pain_gen']["cell_different_color"]
                        if execute == 1:
                            y.energy -= 1
                            y.rotation -= 1
                            y.rotation %= 8
                        elif execute == 2:
                            y.energy -= 1
                            y.rotation += 1
                            y.rotation %= 8
                        elif execute == 3:
                            if world[look_coords[0]][look_coords[1]] == 0:
                                y.energy -= 1
                                world[xi][yi], world[look_coords[0]][look_coords[1]] = world[look_coords[0]][look_coords[1]], world[xi][yi]
                                if cursor_pos == [xi, yi]:
                                    cursor_pos = look_coords
                            elif isinstance(world[look_coords[0]][look_coords[1]], Food):
                                y.energy += world[look_coords[0]][look_coords[1]].energy
                                y.food_eaten += 1
                                world[look_coords[0]][look_coords[1]] = 0
                            elif isinstance(world[look_coords[0]][look_coords[1]], Meat):
                                y.energy += world[look_coords[0]][look_coords[1]].energy
                                y.food_eaten += 1
                                world[look_coords[0]][look_coords[1]] = 0
                            elif isinstance(world[look_coords[0]][look_coords[1]], Cell):
                                if y.energy > world[look_coords[0]][look_coords[1]].energy + y.gens['to_attack_cell']:
                                    y.energy -= 1
                                    y.bites += 1
                                    world[look_coords[0]][look_coords[1]].energy -= BITE_ENERGY
                                    world[look_coords[0]][look_coords[1]].pain = True
                                    if world[look_coords[0]][look_coords[1]].energy <= 0:
                                        y.kills += 1
                                else:
                                    execute = y.gens['pain_gen']["unable_to_attack"]
                                    if execute == 1:
                                        y.energy -= 1
                                        y.rotation -= 1
                                        y.rotation %= 8
                                    if execute == 2:
                                        y.energy -= 1
                                        y.rotation += 1
                                        y.rotation %= 8
                        y.pain = False
                    else:
                        if world[look_coords[0]][look_coords[1]] == 0:
                            execute = y.gens['gens'][y.gen]["none"]
                        elif isinstance(world[look_coords[0]][look_coords[1]], Wall):
                            execute = y.gens['gens'][y.gen]["wall"]
                        elif isinstance(world[look_coords[0]][look_coords[1]], Food):
                            execute = y.gens['gens'][y.gen]["food"]
                        elif isinstance(world[look_coords[0]][look_coords[1]], Meat):
                            execute = y.gens['gens'][y.gen]["meat"]
                        elif isinstance(world[look_coords[0]][look_coords[1]], Cell):
                            if y.gens['color'] == world[look_coords[0]][look_coords[1]].gens['color']:
                                execute = y.gens['gens'][y.gen]["cell_same_color"]
                            else:
                                execute = y.gens['gens'][y.gen]["cell_different_color"]
                        if execute == 1:
                            y.energy -= 1
                            y.rotation -= 1
                            y.rotation %= 8
                        elif execute == 2:
                            y.energy -= 1
                            y.rotation += 1
                            y.rotation %= 8
                        elif execute == 3:
                            if world[look_coords[0]][look_coords[1]] == 0:
                                y.energy -= 1
                                world[xi][yi], world[look_coords[0]][look_coords[1]] = world[look_coords[0]][look_coords[1]], world[xi][yi]
                                if cursor_pos == [xi, yi]:
                                    cursor_pos = look_coords
                            elif isinstance(world[look_coords[0]][look_coords[1]], Food):
                                y.energy += world[look_coords[0]][look_coords[1]].energy
                                y.food_eaten += 1
                                world[look_coords[0]][look_coords[1]] = 0
                            elif isinstance(world[look_coords[0]][look_coords[1]], Meat):
                                y.energy += world[look_coords[0]][look_coords[1]].energy
                                y.food_eaten += 1
                                world[look_coords[0]][look_coords[1]] = 0
                            elif isinstance(world[look_coords[0]][look_coords[1]], Cell):
                                if y.energy > world[look_coords[0]][look_coords[1]].energy + y.gens['to_attack_cell']:
                                    y.energy -= 1
                                    y.bites += 1
                                    world[look_coords[0]][look_coords[1]].energy -= BITE_ENERGY
                                    world[look_coords[0]][look_coords[1]].pain = True
                                    if world[look_coords[0]][look_coords[1]].energy <= 0:
                                        y.kills += 1
                                else:
                                    execute = y.gens['gens'][y.gen]["unable_to_attack"]
                                    if execute == 1:
                                        y.energy -= 1
                                        y.rotation -= 1
                                        y.rotation %= 8
                                    if execute == 2:
                                        y.energy -= 1
                                        y.rotation += 1
                                        y.rotation %= 8
                        y.gen += 1
                        y.gen %= GENS_LEN
                    y.age += 1
        iterations += 1
        food_to_spawn += FOOD_SPAWN_RATE
        for _ in range(int(food_to_spawn)):
            coords = [random.randint(1, WORLD_SIZE[0]-2), random.randint(1, WORLD_SIZE[1]-2)]
            if world[coords[0]][coords[1]] == 0:
                world[coords[0]][coords[1]] = Food(FOOD_ENERGY)
        food_to_spawn -= int(food_to_spawn)
        if cell == 0:
            simulate = False
    clock.tick(FRAMES_PES_SEC)
pygame.quit()