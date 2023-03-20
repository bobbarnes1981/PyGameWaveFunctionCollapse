import logging
import os
import pygame
import random
import time

COLOUR_WHITE = (255,255,255)
COLOUR_RED = (255,0,0)
COLOUR_GREEN = (0,255,0)
COLOUR_YELLOW = (255,255,0)
COLOUR_ORANGE = (255,80,0)

TILE_WIDTH = 32
TILE_HEIGHT = 32
TILE_X = 20
TILE_Y = 20

class TileSet(object):
    def __init__(self, tiles: dict) -> None:
        self._tiles = tiles
        image_path = os.path.dirname(__file__)
        self._images = {}
        for name in self._tiles.keys():
            self._images[name] = pygame.image.load(os.path.join(image_path, 'tiles', '{0}.png'.format(name)))
    def names(self) -> list[str]:
        return list(self._tiles.keys())
    def rule(self, tile_name: str, direction: str) -> dict:
        return self._tiles[tile_name]['rules'][direction]
    def weight(self, tile_name: str) -> int:
        return self._tiles[tile_name]['weight']
    def image(self, tile_name: str) -> pygame.Surface:
        return self._images[tile_name]

class Cell(object):
    def __init__(self, r: int, c: int, choices: list[str]) -> None:
        self._r = r
        self._c = c
        self._choices = choices
    @property
    def choices(self) -> list[str]:
        return self._choices
    @choices.setter
    def choices(self, choices: list[str]):
        self._choices = choices
    @property
    def r(self) -> int:
        return self._r
    @property
    def c(self) -> int:
        return self._c

class Solver(object):
    def __init__(self, tileset: TileSet, wrap=False):
        self._tileset = tileset
        self._wrap = wrap

        self._grid = []
        for r in range(0, TILE_Y):
            self._grid.append([])
            for c in range(0, TILE_X):
                self._grid[r].append([Cell])
                self._grid[r][c] = Cell(r, c, self._tileset.names())
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
        self._firstchanged = None
        self._checked = []
        self._changed = []
    def get_cell(self, r: int, c: int) -> Cell:
        return self._grid[r][c]
    def get_image(self, tile_name: str) -> pygame.Surface:
        return self._tileset.image(tile_name)
    def checked_cells(self) -> list[Cell]:
        return self._checked
    def changed_cells(self) -> list[Cell]:
        return self._changed
    def resolved_cell(self) -> Cell:
        return self._firstchanged
    def solve(self) -> bool:
        """
        For all cells with greater than one choice
        Get all the cells with the lowest number of choices
        Pick a random cell
        Choose once of the tiles available to the cell
        """
        logging.info('solve')
        self._firstchanged = None
        self._checked.clear()
        self._changed.clear()
        # get all cells with more than one choice
        data = [cell for row in self._grid for cell in row if len(cell.choices) > 1]
        # sort by number of choices
        data.sort(key=lambda cell: len(cell.choices), reverse=False)
        logging.info('num cells {0}'.format(len(data)))
        if len(data) > 0:
            # find min choices
            num_choices = len(data[0].choices)
            logging.info('min choices {0}'.format(num_choices))
            # filter for cells with same number of choices
            data = [d for d in data if len(d.choices) == num_choices]
            logging.info('num cells {0}'.format(len(data)))
            # pick random cell with least choices
            cell = random.choice(data)
            # select one of the options
            w = list(map(self._tileset.weight, cell.choices))
            chosen_tile = random.choices(cell.choices, weights=w, k=1)[0]
            # should we check before choosing that it's still valid
            cell.choices = [chosen_tile]
            # flag as first changed
            self._firstchanged = cell
            # resolve neighbourhood
            self.resolve_cell_neighbours(cell)
        return self.is_complete()
    def is_complete(self):
        for r in range(0, TILE_Y):
            for c in range(0, TILE_X):
                if len(self._grid[r][c].choices) > 1:
                    return False
        return True
    def get_cell_in_direction(self, cell: Cell, direction: str) -> Cell:
        """
        Get the cell in the specified direction (n,e,s,w)
        """
        return self._get_cell_dict[direction](cell.r, cell.c)
    def get_north(self, r: int, c: int) -> Cell:
        """
        Get the cell to the north
        """
        x = c
        if r > 0:
            y = r-1
            return self._grid[y][x]
        if self._wrap:
            return self._grid[TILE_Y-1][x]
        return False
    def get_south(self, r: int, c: int) -> Cell:
        """
        Get the cell to the south
        """
        x = c
        if r < TILE_Y-1:
            y = r+1
            return self._grid[y][x]
        if self._wrap:
            return self._grid[0][x]
        return False
    def get_west(self, r: int, c: int) -> Cell:
        """
        Get the cell to the west
        """
        y = r
        if c > 0:
            x = c-1
            return self._grid[y][x]
        if self._wrap:
            return self._grid[y][TILE_X-1]
        return False
    def get_east(self, r: int, c: int) -> Cell:
        """
        Get the cell to the east
        """
        y = r
        if c < TILE_X-1:
            x = c+1
            return self._grid[y][x]
        if self._wrap:
            return self._grid[y][0]
        return False
    def resolve_cell(self, cell: Cell) -> None:
        """
        Update cell with possibilities based on neighbouring cells
        then if this cell has changed repeat the process on the
        neighbouring cells
        """
        logging.info('checking {0},{1}'.format(cell.r,cell.c))
        self._checked.append(cell)
        if len(cell.choices) > 1:
            logging.info('not set')
            has_changed = False
            has_changed |= self.update_allowed_choices(cell, 'n')
            has_changed |= self.update_allowed_choices(cell, 's')
            has_changed |= self.update_allowed_choices(cell, 'w')
            has_changed |= self.update_allowed_choices(cell, 'e')
            logging.info('choices left {0}'.format(len(cell.choices)))
            if has_changed:
                self._changed.append(cell)
                self.resolve_cell_neighbours(cell)
        else:
            logging.info('already set')
    def resolve_cell_neighbours(self, cell: Cell) -> None:
        """
        Resolve cells in von neumann neighbourhood
        """
        self.resolve_cell_neighbour(cell, 'n')
        self.resolve_cell_neighbour(cell, 'e')
        self.resolve_cell_neighbour(cell, 's')
        self.resolve_cell_neighbour(cell, 'w')
    def resolve_cell_neighbour(self, cell: Cell, out_direction: str):
        """
        Resolve cell in specified direction (n,e,s,w)
        """
        c = self.get_cell_in_direction(cell, out_direction)
        if c != False:
            self.resolve_cell(c)
    def update_allowed_choices(self, cell_to_restrict: Cell, out_direction: str) -> bool:
        """
        Update allowed choices for cell_to_restrict based on 
        possibilities in von neumann neighbourhood
        Returns True if the allowed choices has changed
        """
        # if a cell exists in out_direction
        restricter = self.get_cell_in_direction(cell_to_restrict, out_direction)
        if restricter != False:
            logging.debug('checking from {0}'.format(out_direction))
            if len(restricter.choices) > 0:
                if len(restricter.choices) < len(self._tileset.names()):
                    in_direction = self._opposite_direction[out_direction]
                    logging.debug('restricting')
                    # create list of all allowed choices
                    allowed = []
                    for choice in restricter.choices:
                        # get rules that apply from other cell into this cell
                        for allow in self._tileset.rule(choice, in_direction):
                            allowed.append(allow)
                    choices = []
                    # remove all choices not allowed
                    for choice in cell_to_restrict.choices:
                        if choice in allowed:
                            choices.append(choice)
                    if cell_to_restrict.choices != choices:
                        cell_to_restrict.choices = choices
                        return True
        return False

class App(object):
    def __init__(self, solver: Solver, delay: float, shownumbers: bool, showchanged: bool) -> None:
        self._solver = solver
        self._delay = delay
        self._shownumbers = shownumbers
        self._showchanged = showchanged

        self._running = True
        self._display_surf = None
        self._width = TILE_WIDTH * TILE_X
        self._height = TILE_HEIGHT * TILE_Y
        self._size = (self._width, self._height)
        self._time = time.time()
        self._counter = 0
        self._complete = False

        self._image_cache = {}
    def on_init(self) -> None:
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
    def on_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.QUIT:
            self.running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == 27:
                self._running = False
        else:
            logging.debug(event)
    def on_loop(self, elapsed: float) -> None:
        self._counter+=elapsed
        if self._counter > self._delay:
            logging.info("tick")
            self._counter = 0
            if self._complete == False:
                if self._solver.solve():
                    self._complete = True
    def on_render(self) -> None:
        self._display_surf.fill(COLOUR_WHITE)
        for r in range(0, TILE_Y):
            for c in range(0, TILE_X):
                x = c*TILE_WIDTH
                y = r*TILE_HEIGHT
                cell = self._solver.get_cell(r, c)
                num_choices = len(cell.choices)
                if num_choices == 0:
                    pygame.draw.rect(self._display_surf, COLOUR_RED, (x, y, TILE_WIDTH, TILE_HEIGHT))
                elif num_choices == 1:
                    self._display_surf.blit(self._solver.get_image(cell.choices[0]), (x, y))
                elif self._shownumbers:
                    img = self.font_l.render(str(len(cell.choices)), True, (0,0,0))
                    self._display_surf.blit(img, (x+3, y+6))
                else:
                    img = self.get_or_cache_image(cell)
                    self._display_surf.blit(img, (x, y))
        if self._complete == False:
            if self._showchanged:
                for cell in self._solver.checked_cells():
                    x = cell.c * TILE_WIDTH
                    y = cell.r * TILE_HEIGHT
                    pygame.draw.rect(self._display_surf, COLOUR_GREEN, (x, y, TILE_WIDTH, TILE_HEIGHT), 3)
                for cell in self._solver.changed_cells():
                    x = cell.c * TILE_WIDTH
                    y = cell.r * TILE_HEIGHT
                    pygame.draw.rect(self._display_surf, COLOUR_ORANGE, (x, y, TILE_WIDTH, TILE_HEIGHT), 3)
                resolved = self._solver.resolved_cell()
                if resolved != None:
                    x = resolved.c * TILE_WIDTH
                    y = resolved.r * TILE_HEIGHT
                    pygame.draw.rect(self._display_surf, COLOUR_YELLOW, (x, y, TILE_WIDTH, TILE_HEIGHT), 3)
                    text = self.font_s.render('checked cells', True, COLOUR_GREEN)
                    self._display_surf.blit(text, (10, 10))
                    text = self.font_s.render('changed cells', True, COLOUR_ORANGE)
                    self._display_surf.blit(text, (10, 30))
                    text = self.font_s.render('resolved cell', True, COLOUR_YELLOW)
                    self._display_surf.blit(text, (10, 50))
            text = self.font_s.render('images cached: {0}'.format(len(self._image_cache)), True, COLOUR_RED)
            self._display_surf.blit(text, (10, self._height - 20))
        pygame.display.update()
    def get_or_cache_image(self, cell: Cell) -> pygame.Surface:
        key = ','.join(cell.choices)
        if key not in self._image_cache:
            num_choices = len(cell.choices)
            ratio = 255/num_choices
            i = pygame.Surface((TILE_WIDTH, TILE_HEIGHT))
            i.fill(COLOUR_WHITE)
            for choice in cell.choices:
                tile = self._solver.get_image(choice).copy()
                tile.set_alpha(ratio)
                i.blit(tile, (0, 0))
            self._image_cache[key] = i
        return self._image_cache[key]
    def on_cleanup(self) -> None:
        pygame.quit()
    def on_execute(self) -> None:
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
