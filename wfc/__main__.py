import argparse
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
        'nws',
        'nhouse',
        'sea',
        'swa',
        'nwa',
        'nea',
        'nwall',
        'ewall',
        'swall',
        'wwall',
        'nswall',
        'ewwall'
    ]
    # connected tile rules
    road_connect_n = ['ns','nw','ne','nesw','neswew','neswns','new','nes','nws','nhouse']
    road_connect_e = ['ew','se','ne','nesw','neswew','neswns','new','sew','nes']
    road_connect_s = ['ns','se','sw','nesw','neswew','neswns','sew','nes','nws']
    road_connect_w = ['ew','sw','nw','nesw','neswew','neswns','new','sew','nws']
    # not connected tile rules
    blank_connect_n = ['none','nonea','noneb','ew','se','sw','sew','sea','swa','ewall','swall','wwall','ewwall']
    blank_connect_e = ['none','nonea','noneb','ns','sw','nw','nws','nhouse','swa','nwa','nwall','swall','wwall','nswall']
    blank_connect_s = ['none','nonea','noneb','ew','nw','ne','new','nhouse','nwa','nea','nwall','ewall','wwall','ewwall']
    blank_connect_w = ['none','nonea','noneb','ns','se','ne','nes','nhouse','nea','sea','nwall','ewall','swall','nswall']
    tile_rules = {
        'nesw': { 'n': road_connect_n, 'e': road_connect_e, 's': road_connect_s, 'w': road_connect_w },
        'neswew': { 'n': road_connect_n, 'e': road_connect_e, 's': road_connect_s, 'w': road_connect_w },
        'neswns': { 'n': road_connect_n, 'e': road_connect_e, 's': road_connect_s, 'w': road_connect_w },
        'ew': { 'n': blank_connect_n, 'e': road_connect_e, 's': blank_connect_s, 'w': road_connect_w },
        'ns': { 'n': road_connect_n, 'e': blank_connect_e, 's': road_connect_s, 'w': blank_connect_w },
        'none': { 'n': blank_connect_n, 'e': blank_connect_e, 's': blank_connect_s, 'w': blank_connect_w },
        'nonea': { 'n': blank_connect_n, 'e': blank_connect_e, 's': blank_connect_s, 'w': blank_connect_w },
        'noneb': { 'n': blank_connect_n, 'e': blank_connect_e, 's': blank_connect_s, 'w': blank_connect_w },
        'se': { 'n': road_connect_n, 'e': blank_connect_e, 's': blank_connect_s, 'w': road_connect_w },
        'sw': { 'n': road_connect_n, 'e': road_connect_e, 's': blank_connect_s, 'w': blank_connect_w },
        'nw': { 'n': blank_connect_n, 'e': road_connect_e, 's': road_connect_s, 'w': blank_connect_w },
        'ne': { 'n': blank_connect_n, 'e': blank_connect_e, 's': road_connect_s, 'w': road_connect_w },
        'new': { 'n': blank_connect_n, 'e': road_connect_e, 's': road_connect_s, 'w': road_connect_w },
        'sew': { 'n': road_connect_n, 'e': road_connect_e, 's': blank_connect_s, 'w': road_connect_w },
        'nes': { 'n': road_connect_n, 'e': blank_connect_e, 's': road_connect_s, 'w': road_connect_w },
        'nws': { 'n': road_connect_n, 'e': road_connect_e, 's': road_connect_s, 'w': blank_connect_w },
        'nhouse': { 'n': blank_connect_n, 'e': blank_connect_e, 's': road_connect_s, 'w': blank_connect_w },
        'sea': { 'n': ['nea'], 'e': blank_connect_e, 's': blank_connect_s, 'w': ['swa'] },
        'swa': { 'n': ['nwa'], 'e': ['sea'], 's': blank_connect_s, 'w': blank_connect_w },
        'nwa': { 'n': blank_connect_n, 'e': ['nea'], 's': ['swa'], 'w': blank_connect_w },
        'nea': { 'n': blank_connect_n, 'e': blank_connect_e, 's': ['sea'], 'w': ['nwa'] },
        'nwall': { 'n': blank_connect_n, 'e': blank_connect_e, 's': ['swall','nswall'], 'w': blank_connect_w },
        'ewall': { 'n': blank_connect_n, 'e': blank_connect_e, 's': blank_connect_s, 'w': ['wwall','ewwall'] },
        'swall': { 'n': ['nwall','nswall'], 'e': blank_connect_e, 's': blank_connect_s, 'w': blank_connect_w },
        'wwall': { 'n': blank_connect_n, 'e': ['ewall','ewwall'], 's': blank_connect_s, 'w': blank_connect_w },
        'nswall': { 'n': ['nwall','nswall'], 'e': blank_connect_e, 's': ['swall','nswall'], 'w': blank_connect_w },
        'ewwall': { 'n': blank_connect_n, 'e': ['ewall','ewwall'], 's': blank_connect_s, 'w': ['wwall','ewwall'] }
    }
    tileset = solver.TileSet(tile_names, tile_rules)

    a = solver.App(tileset, args.delay, args.shownumbers)
    a.on_execute()