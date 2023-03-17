import logging
import os
import pygame
import random
import time

COLOUR_WHITE = (255,255,255)
COLOUR_RED = (255,0,0)

# hack to try and reduce failures
NUMBER_OF_PASSES = 2

TILE_WIDTH = 32
TILE_HEIGHT = 32
TILE_X = 20
TILE_Y = 20

class TileSet(object):
    def __init__(self, tiles):
        self._tiles = tiles
        image_path = os.path.dirname(__file__)
        self._images = {}
        for name in self._tiles.keys():
            self._images[name] = pygame.image.load(os.path.join(image_path, 'tiles', '{0}.png'.format(name)))
    def names(self):
        return list(self._tiles.keys())
    def rule(self, tile_name, direction):
        return self._tiles[tile_name]['rules'][direction]
    def weight(self, tile_name):
        return self._tiles[tile_name]['weight']
    def image(self, tile_name):
        return self._images[tile_name]

class App(object):
    def __init__(self, tileset, delay, shownumbers):
        self._tileset = tileset
        self._delay = delay
        self._shownumbers = shownumbers

        self._grid = []
        for r in range(0, TILE_Y):
            self._grid.append([])
            for c in range(0, TILE_X):
                self._grid[r].append([])
                self._grid[r][c] = {
                    'choices': self._tileset.names(),
                    'x': c,
                    'y': r
                }

        self._running = True
        self._display_surf = None
        self._width = TILE_WIDTH * TILE_X
        self._height = TILE_HEIGHT * TILE_Y
        self._size = (self._width, self._height)
        self._time = time.time()
        self._counter = 0
        self._complete = False
        self._get_cell_dict = {
            'n': self.get_north,
            'e': self.get_east,
            's': self.get_south,
            'w': self.get_west
        }
        self._opposite_direction = {
            'n': 's',
            'e': 'w',
            's': 'n',
            'w': 'e'
        }
        self._image_cache = {}
    def on_init(self):
        pygame.init()
        pygame.display.set_caption("Solver")
        self._display_surf = pygame.display.set_mode(self._size, pygame.HWSURFACE | pygame.DOUBLEBUF)
        self._running = True
        #self.font = pygame.font.SysFont('courier.ttf', 72)
        font_name = pygame.font.get_default_font()
        logging.info("System font: {0}".format(font_name))
        self.font_s = pygame.font.SysFont(None, 22)
        self.font_l = pygame.font.SysFont(None, 33)
        return True
    def on_event(self, event):
        if event.type == pygame.QUIT:
            self.running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == 27:
                self._running = False
        else:
            logging.debug(event)
    def on_loop(self, elapsed):
        self._counter+=elapsed
        if self._counter > self._delay:
            logging.info("tick")
            self._counter = 0
            if self._complete == False:
                if self.solve():
                    self._complete = True
    def solve(self):
        logging.info('solve')

        # get all cells with more than one choice
        data = []
        for r in range(0, TILE_Y):
            for c in range(0, TILE_X):
                cell = self._grid[r][c]
                if len(cell['choices']) > 1:
                    data.append(cell)

        # sort by number of choices
        data.sort(key=lambda cell: len(cell['choices']), reverse=False)
        logging.info('num cells {0}'.format(len(data)))

        if len(data) > 0:

            # find min choices
            num_choices = len(data[0]['choices'])
            logging.info('min choices {0}'.format(num_choices))

            # filter for cells with same number of choices
            data = [d for d in data if len(d['choices']) == num_choices]
            logging.info('num cells {0}'.format(len(data)))

            # pick random cell with least choices
            cell = random.choice(data)

            # select one of the options
            chosen_tile = random.choices(cell['choices'], weights=map(self._tileset.weight, cell['choices']), k=1)[0]
            #chosen_tile = random.choice(cell['choices'])

            # should we check before choosing that it's still valid
            cell['choices'] = [chosen_tile]

            self.resolve_cells()
        return False
    def resolve_cells(self):
        # resolve cells
        for p in range(0, NUMBER_OF_PASSES):
            for r in range(0, TILE_Y):
                for c in range(0, TILE_X):
                    self.resolve_cell(r, c)
    def resolve_cell(self, r, c):
        logging.info('checking {0},{1}'.format(r,c))
        cell = self._grid[r][c]
        if len(cell['choices']) > 1:
            logging.info('not set')
            self.update_allowed_choices(cell, 'n')
            self.update_allowed_choices(cell, 's')
            self.update_allowed_choices(cell, 'w')
            self.update_allowed_choices(cell, 'e')
            logging.info('choices left {0}'.format(len(cell['choices'])))
        else:
            logging.info('already set')
    def update_allowed_choices(self, cell_to_restrict, out_direction):
        # if a cell exists in out_direction
        restricter = self.get_cell(cell_to_restrict['y'], cell_to_restrict['x'], out_direction)
        if restricter != False:
            in_direction = self._opposite_direction[out_direction]
            logging.debug('checking from {0}'.format(in_direction))
            if len(restricter['choices']) > 0:
                if len(restricter['choices']) < len(self._tileset.names()):
                    logging.debug('restricting')
                    # create list of all allowed choices
                    allowed = []
                    for choice in restricter['choices']:
                        # get rules that apply from other cell into this cell
                        for allow in self._tileset.rule(choice, in_direction):
                            allowed.append(allow)
                    choices = []
                    # remove all choices not allowed
                    for choice in cell_to_restrict['choices']:
                        if choice in allowed:
                            choices.append(choice)
                    cell_to_restrict['choices'] = choices
    def get_cell(self, r, c, direction):
        return self._get_cell_dict[direction](r, c)
    def get_north(self, r, c):
        if r > 0:
            x = c
            y = r-1
            return self._grid[y][x]
        return False
    def get_south(self, r, c):
        if r < TILE_Y-1:
            x = c
            y = r+1
            return self._grid[y][x]
        return False
    def get_west(self, r, c):
        if c > 0:
            x = c-1
            y = r
            return self._grid[y][x]
        return False
    def get_east(self, r, c):
        if c < TILE_X-1:
            x = c+1
            y = r
            return self._grid[y][x]
        return False
    def on_render(self):
        self._display_surf.fill(COLOUR_WHITE)
        for r in range(0, TILE_Y):
            for c in range(0, TILE_X):
                x = c*TILE_WIDTH
                y = r*TILE_HEIGHT
                cell = self._grid[r][c]
                num_choices = len(cell['choices'])
                if num_choices == 0:
                    pygame.draw.rect(self._display_surf, COLOUR_RED, (x, y, TILE_WIDTH, TILE_HEIGHT))
                elif num_choices == 1:
                    self._display_surf.blit(self._tileset.image(cell['choices'][0]), (x, y))
                elif self._shownumbers:
                    img = self.font_l.render(str(len(cell['choices'])), True, (0,0,0))
                    self._display_surf.blit(img, (x+3, y+6))
                else:
                    for choice in cell['choices']:
                        img = self.get_image(cell, choice)
                        self._display_surf.blit(img, (x, y))
        pygame.display.update()
    def get_image(self, cell, choice):
        num_choices = len(cell['choices'])
        ratio = 255/num_choices
        if choice not in self._image_cache.keys():
            self._image_cache[choice] = {}
        if num_choices not in self._image_cache[choice].keys():
            i = self._tileset.image(choice).copy()
            i.set_alpha(ratio)
            self._image_cache[choice][num_choices] = i
        return self._image_cache[choice][num_choices]
    def on_cleanup(self):
        pygame.quit()
    def on_execute(self):
        if self.on_init() == False:
            self._running = False
        while self._running:
            current = time.time()
            elapsed = current - self._time
            self._time = current
            for event in pygame.event.get():
                self.on_event(event)
            self.on_loop(elapsed)
            self.on_render()
        self.on_cleanup()
