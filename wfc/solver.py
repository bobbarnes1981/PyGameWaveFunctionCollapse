import logging
import os
import pygame
import random
import time

COLOUR_WHITE = (255,255,255)

TILE_WIDTH = 32
TILE_HEIGHT = 32
TILE_X = 10
TILE_Y = 10

image_path = os.path.dirname(__file__)

tile_names = [
    'cross',
    'h',
    'v',
    'none',
    'r-n',
    'r-e',
    'r-s',
    'r-w'
]

# tile images
images = {}
for tile_name in tile_names:
    images[tile_name] = pygame.image.load(os.path.join(image_path, 'tiles', '{0}.png'.format(tile_name)))

# grid for display
grid = []
for r in range(0, TILE_Y):
    grid.append([])
    for c in range(0, TILE_X):
        grid[r].append([])
        grid[r][c] = {
            'choices': tile_names,
            'x': c,
            'y': r
        }

# allowed tile rules
n_list = ['v','r-s','r-w','cross']
e_list = ['h','r-n','r-w','cross']
w_list = ['h','r-e','r-s','cross']
s_list = ['v','r-n','r-e','cross']
n__list = ['none','h', 'r-n','r-e']
e__list = ['none','v','r-e','r-s']
s__list = ['none','h','r-s','r-w']
w__list = ['none','v','r-n','r-w']
rules = {
    'cross': {
        'n': n_list,
        'e': e_list,
        's': s_list,
        'w': w_list
    },
    'h': {
        'n': n__list,
        'e': e_list,
        's': s__list,
        'w': w_list
    },
    'v': {
        'n': n_list,
        'e': e__list,
        's': s_list,
        'w': w__list
    },
    'none': {
        'n': n__list,
        'e': e__list,
        's': s__list,
        'w': w__list
    },
    'r-n': {
        'n': n_list,
        'e': e__list,
        's': s__list,
        'w': w_list
    },
    'r-e': {
        'n': n_list,
        'e': e_list,
        's': s__list,
        'w': w__list
    },
    'r-s': {
        'n': n__list,
        'e': e_list,
        's': s_list,
        'w': w__list
    },
    'r-w': {
        'n': n__list,
        'e': e__list,
        's': s_list,
        'w': w_list
    }
}

class App(object):
    def __init__(self, delay):
        self._delay = delay
        self._running = True
        self._display_surf = None
        self._width = TILE_WIDTH * TILE_X
        self._height = TILE_HEIGHT * TILE_Y
        self._size = (self._width, self._height)
        self._time = time.time()
        self._counter = 0
        self._complete = False
    def on_init(self):
        pygame.init()
        pygame.display.set_caption("Solver")
        self._display_surf = pygame.display.set_mode(self._size, pygame.HWSURFACE | pygame.DOUBLEBUF)
        self._running = True
        #self.font = pygame.font.SysFont('courier.ttf', 72)
        font_name = pygame.font.get_default_font()
        logging.info("System font: {0}".format(font_name))
        self.font_s = pygame.font.SysFont(None, 22)
        self.font_l = pygame.font.SysFont(None, 66)
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
                cell = grid[r][c]
                if len(cell['choices']) > 1:
                    data.append(cell)

        # sort by number of choices
        data.sort(key=lambda cell: len(cell['choices']), reverse=False)
        logging.info('num cells {0}'.format(len(data)))

        if len(data) > 0:

            # find min choices
            num_choices = data[0]['choices']
            logging.info('min choices {0}'.format(num_choices))

            # filter for cells with same number of choices
            data = [d for d in data if d['choices'] == num_choices]
            logging.info('num cells {0}'.format(len(data)))

            # pick random cell with least choices
            cell = random.choice(data)

            # select one of the options
            chosen_tile = random.choice(cell['choices'])

            cell['choices'] = [chosen_tile]

            # resolve cells
            for r in range(0, TILE_Y):
                for c in range(0, TILE_X):
                    cell = grid[r][c]
                    logging.info('checking {0},{1}'.format(r,c))
                    if len(cell['choices']) > 1:
                        logging.info('not set')
                        if r > 0:
                            logging.debug('checking north')
                            x = c
                            y = r-1
                            n = grid[y][x]
                            if len(n['choices']) == 1:
                                logging.debug('restricting')
                                allowed = rules[n['choices'][0]]['s']
                                choices = []
                                for choice in cell['choices']:
                                    if choice in allowed:
                                        choices.append(choice)
                                cell['choices'] = choices
                        if r < TILE_Y-1:
                            logging.debug('checking south')
                            x = c
                            y = r+1
                            s = grid[y][x]
                            if len(s['choices']) == 1:
                                logging.debug('restricting')
                                allowed = rules[s['choices'][0]]['n']
                                choices = []
                                for choice in cell['choices']:
                                    if choice in allowed:
                                        choices.append(choice)
                                cell['choices'] = choices
                        if c > 0:
                            logging.debug('checking west')
                            x = c-1
                            y = r
                            w = grid[y][x]
                            if len(w['choices']) == 1:
                                logging.debug('restricting')
                                allowed = rules[w['choices'][0]]['e']
                                choices = []
                                for choice in cell['choices']:
                                    if choice in allowed:
                                        choices.append(choice)
                                cell['choices'] = choices
                        if c < TILE_X-1:
                            logging.debug('checking east')
                            x = c+1
                            y = r
                            e = grid[y][x]
                            if len(e['choices']) == 1:
                                logging.debug('restricting')
                                allowed = rules[e['choices'][0]]['w']
                                choices = []
                                for choice in cell['choices']:
                                    if choice in allowed:
                                        choices.append(choice)
                                cell['choices'] = choices
                        logging.info('choices left {0}'.format(len(cell['choices'])))
                    else:
                        logging.info('already set')

#            print(cell)
#            print(grid)
#            exit()

        return False
    def on_render(self):
        self._display_surf.fill(COLOUR_WHITE)
        for r in range(0, TILE_Y):
            for c in range(0, TILE_X):
                x = c*TILE_WIDTH
                y = r*TILE_HEIGHT
                cell = grid[r][c]
                if len(cell['choices']) == 1:
                    self._display_surf.blit(images[cell['choices'][0]], (x, y))
                else:
                    img = self.font_l.render(str(len(cell['choices'])), True, (0,0,0))
                    self._display_surf.blit(img, (x, y))
        pygame.display.update()
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
