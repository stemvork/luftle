import pygame
import sys
import math, random

pygame.init()

FPS = 30
clock = pygame.time.Clock()

screen = pygame.display.set_mode(flags=pygame.FULLSCREEN)

WIDTH = 50

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

    def set_shape(self, shape=None):
        if shape is None:
            if self.shape < 5:
                self.shape += 1
            else:
                self.shape = 0

    def render(self):
        self.image.fill(BLACK)
        colour      = pygame.Color(COLOURS[self.colour])
        center      = WIDTH // 2
        rect_offset = 7
        circ_offset = 6
        diam_offset = 5
        x_offset    = 6
        x_width     = 6
        star_offset = 3
        flow_c_off  = 11
        flow_r      = center // 2 - 4
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
    def __init__(self, tileset=None):
        self.tiles = []
        if tileset is not None:
            self.deal(tileset)

    def deal(self, tileset):
        for i in range(6):
            self.add(tileset.pop())

    def add(self, tile):
        self.tiles.append(tile)
    
    def remove(self, tile):
        i = self.tiles.index(tile)
        return self.tiles.pop(i)
    
    def draw(self, _screen, height=0):
        for index, tile in enumerate(self.tiles):
            tile.move_grid((index, height))
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

def l_check_att(placed, cursor):
    if len(placed) == 0:
        return True
    if not l_check_occ(placed, cursor):
        if l_has_neigh(placed, cursor):
            return True
    return False

def l_place_cursor_att(placed, cursor):
    if l_check_att(placed, cursor):
        placed.append(cursor)
        cursor = Tile((0, 0))
    return placed, cursor

cursor = Tile()
cursor.move((2, 2))

tileset = []
for i in range(6):
    for j in range(6):
        for k in range(3):
            tileset.append(Tile((i, j)))
random.shuffle(tileset)

rack = Rack(tileset)
print([(rack.tiles[i].shape, rack.tiles[i].colour) for i in range(len(rack.tiles))])

placed = []

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            proper_exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                proper_exit()
            # c, s, space are test functions now
            # space should select next tile
            # enter should confirm placement and switch player
            # TODO player has rack, has name, has score
            elif event.key == pygame.K_c:
                cursor.set_colour()
                cursor.render()
            elif event.key == pygame.K_s:
                cursor.set_shape()
                cursor.render()
            elif event.key == pygame.K_SPACE:
                pass
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if pygame.mouse.get_pressed()[0]:
                # placed, cursor = l_place_cursor(placed, cursor)
                # placed, cursor = l_place_cursor_not_occ(placed, cursor)
                placed, cursor = l_place_cursor_att(placed, cursor)


    screen.fill(BG)

    # TODO large count of remaining tiles
    # TODO Scoreboard
    # TODO Two players/racks

    cursor.move_snap_first(pygame.mouse.get_pos())

    draw_grid(screen)
    cursor.draw(screen)

    rack.draw(screen)
    draw_list(screen, placed)

    pygame.display.flip()
    clock.tick(FPS)

