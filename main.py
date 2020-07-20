# TODO start work on legal move check (color or shape match, not both)

import pygame
import sys
import math, random

pygame.init()

FPS = 30
clock = pygame.time.Clock()

DEBUG = True

if DEBUG:
    screen = pygame.display.set_mode((600, 600))
    font   = pygame.font.SysFont("Arial", 128, True)
    WIDTH = 20

else:
    screen = pygame.display.set_mode(flags=pygame.FULLSCREEN)
    font   = pygame.font.SysFont("Arial", 320, True)
    WIDTH = 50

sw     = screen.get_width()
sh     = screen.get_height()
CENTER = (sw//2, sh//2)


BLACK = (0, 0, 0)
BG    = (20, 50, 80)
GRAY  = (100, 100, 100)
WHITE = (255, 255, 255)
COLOURS = [(255, 0, 0), (0, 0, 255), 
        (0, 180, 0), (255, 255, 0), 
        (255, 0, 255), (0, 255, 255)]

NEIGHS = [(-1, 0), (1, 0), (0, -1), (0, 1)]

class Tile:
    def __init__(self, colshape=(0, 0)):
        self.x = 0
        self.y = 0
        self.colour = colshape[0]
        self.shape  = colshape[1]
        self.colshape = colshape
        self.image = pygame.Surface((WIDTH, WIDTH))
        self.rect  = self.image.get_rect()
        self.image.fill(WHITE)
        self.render()

    def move(self, pos):
        self.x += pos[0]
        self.y += pos[1]
        rpos   = pos[0] * WIDTH, pos[1] * WIDTH
        self.rect.move_ip(rpos)

    def move_grid(self, pos):
        x, y   = pos
        self.x = x
        self.y = y
        rpos   = x * WIDTH, y * WIDTH
        self.rect.topleft = 0, 0
        self.rect.move_ip(rpos)

    def move_snap_first(self, pos):
        x, y = snap_to_grid(pos)
        self.move_grid((x, y))

    def draw(self, _screen):
        _screen.blit(self.image, self.rect)

    def set_colour(self, colour=None):
        if colour is None:
            if self.colour < len(COLOURS) - 1:
                self.colour += 1
            else:
                self.colour = 0
        self.colshape = (self.colshape[0], self.colour)

    def set_shape(self, shape=None):
        if shape is None:
            if self.shape < 5:
                self.shape += 1
            else:
                self.shape = 0
        self.colshape = (self.shape, self.colshape[1])

    def render(self):
        self.image.fill(BLACK)
        colour      = pygame.Color(COLOURS[self.colour])
        center      = WIDTH // 2
        rect_offset = 7/50 * WIDTH
        circ_offset = 6/50 * WIDTH
        diam_offset = 5/50 * WIDTH
        x_offset    = 6/50 * WIDTH
        x_width     = 6/50 * WIDTH
        star_offset = 3/50 * WIDTH
        flow_c_off  = 11/50 * WIDTH
        flow_r      = center // 2 - 4/50 * WIDTH
        if self.shape == 0:
            pygame.draw.rect(self.image, colour,
                    (rect_offset, rect_offset, 
                        WIDTH - 2 * rect_offset, WIDTH - 2 * rect_offset))
        elif self.shape == 1:
            pygame.draw.circle(self.image, colour,
                    (center, center), WIDTH//2 - circ_offset)
        elif self.shape == 2:
            pts = [(center, diam_offset), 
                    (diam_offset, center),
                    (center, WIDTH - diam_offset), 
                    (WIDTH - diam_offset, center)]
            pygame.draw.polygon(self.image, colour, pts)
        elif self.shape == 3:
            pts = [(x_offset, x_offset),
                    (center + x_width, center - x_width),
                    (WIDTH - x_offset, WIDTH - x_offset),
                    (center - x_width, center + x_width)]
            pygame.draw.polygon(self.image, colour, pts)
            
            pts = [(x_offset, WIDTH - x_offset),
                    (center + x_width, center + x_width),
                    (WIDTH - x_offset, x_offset),
                    (center - x_width, center - x_width)]
            pygame.draw.polygon(self.image, colour, pts)
        elif self.shape == 4:
            r   = center - star_offset
            pts = [(center + r * math.cos(3 * i * 45 * math.pi / 180),
                center + r * math.sin(3 * i * 45 * math.pi / 180))
                for i in range(8)]
            pygame.draw.polygon(self.image, colour, pts)
            pygame.draw.circle(self.image, colour, (center, center), r // 2 + 1)
        elif self.shape == 5:
            c   = [(center + flow_c_off, center),
                    (center - flow_c_off, center),
                    (center, center - flow_c_off),
                    (center, center + flow_c_off)]
            [pygame.draw.circle(self.image, colour, _c, flow_r) for _c in c]
            pygame.draw.circle(self.image, colour, (center, center), flow_r + 1)

class Rack:
    def __init__(self, tileset=None, yh=0):
        self.tiles  = []
        self.height = yh
        if tileset is not None:
            self.deal(tileset)

    def deal(self, tileset):
        dn = 6 - len(self.tiles)
        for i in range(dn):
            self.add(tileset.pop())

    def add(self, tile):
        self.tiles.append(tile)
    
    def remove(self, tile):
        i = self.tiles.index(tile)
        return self.tiles.pop(i)
    
    def draw(self, _screen):
        for index, tile in enumerate(self.tiles):
            tile.move_grid((index, self.height))
            tile.draw(_screen)

# UI RELATED
def proper_exit():
    pygame.quit()
    sys.exit()

# DRAWING RELATED
def draw_grid(_screen):
    sw = _screen.get_rect().width
    sh = _screen.get_rect().height
    for i in range(1, sh // WIDTH):
        pygame.draw.line(_screen, GRAY, (0, i*WIDTH), (sw, i*WIDTH))
    for j in range(1, sw // WIDTH):
        pygame.draw.line(_screen, GRAY, (j*WIDTH, 0), (j*WIDTH, sh))

def snap_to_grid(_pos):
    x = math.floor(_pos[0] // WIDTH)
    y = math.floor(_pos[1] // WIDTH)
    return x, y

def draw_list(_screen, _list):
    for index, tile in enumerate(_list):
        tile.draw(_screen)

# LOGIC RELATED
def l_place_cursor(placed, cursor):
    placed.append(cursor)
    cursor = Tile((0, 0))
    return placed, cursor

def l_check_occ(placed, _tile):
    for tile in placed:
        if tile.x == _tile.x and tile.y == _tile.y:
            return True
    return False    

def l_place_cursor_not_occ(placed, cursor):
    if not l_check_occ(placed, cursor):
        placed.append(cursor)
        cursor = Tile((0, 0))
    return placed, cursor

def l_has_neigh(placed, _tile):
    for tile in placed:
        dx = tile.x - _tile.x
        dy = tile.y - _tile.y
        if (dx, dy) in NEIGHS:
            return True
    return False

def l_valid_neigh(placed, _tile):
    flags = []
    for tile in placed:
        dx = tile.x - _tile.x
        dy = tile.y - _tile.y
        if (dx, dy) in NEIGHS:
            _flag = True
            if tile.colshape == _tile.colshape: # identical
                _flag = False
                print("IDENTICAL", tile.colshape)
            elif tile.colour != _tile.colour and tile.shape != _tile.shape:
                _flag = False # incompatible
                print("INCOMPATIBLE", tile.colshape)
            flags.append(_flag)
    print("flags", flags)
    return min(flags)

def l_check_att(placed, cursor):
    if len(placed) == 0:
        return True
    if not l_check_occ(placed, cursor):
        if l_has_neigh(placed, cursor):
            if l_valid_neigh(placed, cursor):
                return True
    return False

def l_place_cursor_att(placed, cursor, racks, selected):
    if len(racks[selected[0]].tiles) > 0:
        if l_check_att(placed, cursor):
            placed.append(cursor)
            placed[-1].move_snap_first(pygame.mouse.get_pos())
            cursor, racks, selected = l_next_tile(cursor, racks, selected)
            racks[selected[0]].remove(placed[-1])
    return placed, cursor, racks, selected

def l_next_player(cursor, racks, selected):
    racks[selected[0]].deal(tileset)

    if selected[0] < len(racks) - 1:
        selected[0] += 1
    else:
        selected[0] = 0
    selected[1] = 0

    if len(racks[selected[0]].tiles) > 0:
        cursor = racks[selected[0]].tiles[selected[1]]
    return cursor, racks, selected

def l_next_tile(cursor, racks, selected):
    if selected[1] < len(racks[selected[0]].tiles) - 1:
        selected[1] += 1
    else:
        selected[1] = 0

    if len(racks[selected[0]].tiles) == 1:
        cursor = None
    else:
        cursor = racks[selected[0]].tiles[selected[1]]

    return cursor, racks, selected

tileset = []
for i in range(6):
    for j in range(6):
        for k in range(3):
            tileset.append(Tile((i, j)))
random.shuffle(tileset)

racks = []
for i in range(2):
    racks.append(Rack(tileset, i))

placed = []
scores = [0, 0]
selected = [0, 0]
cursor = racks[selected[0]].tiles[0]

while True:
    if cursor is not None:
        cursor.move_snap_first(pygame.mouse.get_pos())

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            proper_exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                proper_exit()
            elif event.key == pygame.K_c:
                cursor.set_colour()
                cursor.render()
            elif event.key == pygame.K_s:
                cursor.set_shape()
                cursor.render()
            elif event.key == pygame.K_SPACE:
                cursor, racks, selected = l_next_tile(cursor, racks, selected)
            elif event.key == pygame.K_RETURN:
                cursor, racks, selected = l_next_player(cursor, racks, selected)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if pygame.mouse.get_pressed()[0]:
                # placed, cursor = l_place_cursor(placed, cursor)
                # placed, cursor = l_place_cursor_not_occ(placed, cursor)
                placed, cursor, racks, selected = \
                    l_place_cursor_att(placed, cursor, racks, selected)


    screen.fill(BG)

    count_text = font.render(str(len(tileset)), True, WHITE)
    count_text_rect = count_text.get_rect(center = CENTER)
    screen.blit(count_text, count_text_rect)

    for index, score in enumerate(scores):
        score_colour = WHITE if index is not selected[0] else COLOURS[0]
        score_text = font.render(str(score), True, score_colour)
        score_text_rect = score_text.get_rect(center = 
                (4*WIDTH, sh//4 + sh//2 * index))
        screen.blit(score_text, score_text_rect)

    draw_grid(screen)
    if cursor is not None:
        cursor.draw(screen)

    for rack in racks:
        rack.draw(screen)

    draw_list(screen, placed)

    pygame.display.flip()
    clock.tick(FPS)

