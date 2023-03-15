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
        'neswew',
        'neswns',
        'ew',
        'ns',
        'none',
        'nonea',
        'noneb',
        'se',
        'sw',
        'nw',
        'ne',
        'new',
        'sew',
        'nes',
        'nws'
    ]
    # connected tile rules
    n_list = ['ns','nw','ne','nesw','neswew','neswns','new','nes','nws']
    e_list = ['ew','se','ne','nesw','neswew','neswns','new','sew','nes']
    s_list = ['ns','se','sw','nesw','neswew','neswns','sew','nes','nws']
    w_list = ['ew','sw','nw','nesw','neswew','neswns','new','sew','nws']
    # not connected tile rules
    n__list = ['none','nonea','noneb','ew','se','sw','sew']
    e__list = ['none','nonea','noneb','ns','sw','nw','nws']
    s__list = ['none','nonea','noneb','ew','nw','ne','new']
    w__list = ['none','nonea','noneb','ns','se','ne','nes']
    tile_rules = {
        'nesw': { 'n': n_list, 'e': e_list, 's': s_list, 'w': w_list },
        'neswew': { 'n': n_list, 'e': e_list, 's': s_list, 'w': w_list },
        'neswns': { 'n': n_list, 'e': e_list, 's': s_list, 'w': w_list },
        'ew': { 'n': n__list, 'e': e_list, 's': s__list, 'w': w_list },
        'ns': { 'n': n_list, 'e': e__list, 's': s_list, 'w': w__list },
        'none': { 'n': n__list, 'e': e__list, 's': s__list, 'w': w__list },
        'nonea': { 'n': n__list, 'e': e__list, 's': s__list, 'w': w__list },
        'noneb': { 'n': n__list, 'e': e__list, 's': s__list, 'w': w__list },
        'se': { 'n': n_list, 'e': e__list, 's': s__list, 'w': w_list },
        'sw': { 'n': n_list, 'e': e_list, 's': s__list, 'w': w__list },
        'nw': { 'n': n__list, 'e': e_list, 's': s_list, 'w': w__list },
        'ne': { 'n': n__list, 'e': e__list, 's': s_list, 'w': w_list },
        'new': { 'n': n__list, 'e': e_list, 's': s_list, 'w': w_list },
        'sew': { 'n': n_list, 'e': e_list, 's': s__list, 'w': w_list },
        'nes': { 'n': n_list, 'e': e__list, 's': s_list, 'w': w_list },
        'nws': { 'n': n_list, 'e': e_list, 's': s_list, 'w': w__list }
    }
    tileset = solver.TileSet(tile_names, tile_rules)

    a = solver.App(tileset, args.delay, args.shownumbers)
    a.on_execute()