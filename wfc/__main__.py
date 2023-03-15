import argparse
import json
import logging
import solver

if __name__ == '__main__':
    loglevels = [
        'DEBUG',
        'INFO',
        'WARNING',
        'ERROR',
        'CRITICAL'
    ]

    parser = argparse.ArgumentParser(description='solve sudoku')
    parser.add_argument('-d', '--delay', type=float, required=False, default=1.0, dest='delay')
    parser.add_argument('-l', '--logging', type=str, required=False, default='ERROR', dest='logging', choices=loglevels)
    parser.add_argument('--shownumbers', required=False, default=False, dest='shownumbers', action='store_true')
    args = parser.parse_args()
    
    loglevel = getattr(logging, args.logging, None)
    logging.basicConfig(level=loglevel, format='%(asctime)s %(levelname)s %(name)s %(message)s')

    tile_names = [
        'nesw',
        'ew',
        'ns',
        'none',
        'se',
        'sw',
        'nw',
        'ne'
    ]
    # connected tile rules
    n_list = ['ns','nw','ne','nesw']
    e_list = ['ew','se','ne','nesw']
    s_list = ['ns','se','sw','nesw']
    w_list = ['ew','sw','nw','nesw']
    # not connected tile rules
    n__list = ['none','ew', 'se','sw']
    e__list = ['none','ns','sw','nw']
    s__list = ['none','ew','nw','ne']
    w__list = ['none','ns','se','ne']
    tile_rules = {
        'nesw': {
            'n': n_list,
            'e': e_list,
            's': s_list,
            'w': w_list
        },
        'ew': {
            'n': n__list,
            'e': e_list,
            's': s__list,
            'w': w_list
        },
        'ns': {
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
        'se': {
            'n': n_list,
            'e': e__list,
            's': s__list,
            'w': w_list
        },
        'sw': {
            'n': n_list,
            'e': e_list,
            's': s__list,
            'w': w__list
        },
        'nw': {
            'n': n__list,
            'e': e_list,
            's': s_list,
            'w': w__list
        },
        'ne': {
            'n': n__list,
            'e': e__list,
            's': s_list,
            'w': w_list
        }
    }
    tileset = solver.TileSet(tile_names, tile_rules)

    a = solver.App(tileset, args.delay, args.shownumbers)
    a.on_execute()