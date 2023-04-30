"""Wave function collapse"""

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
    parser.add_argument('--showchanged', required=False, default=False, dest='showchanged', action='store_true')
    parser.add_argument('--wrap', required=False, default=False, dest='wrap', action='store_true')
    args = parser.parse_args()

    loglevel = getattr(logging, args.logging, None)
    logging.basicConfig(level=loglevel, format='%(asctime)s %(levelname)s %(name)s %(message)s')

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
    # wall connect rules
    wall_connect_n = ['nwall','nswall']
    wall_connect_e = ['ewall','ewwall']
    wall_connect_s = ['swall','nswall']
    wall_connect_w = ['wwall','ewwall']
    tiles = {
        'nesw': { 'rules': { 'n': road_connect_n, 'e': road_connect_e, 's': road_connect_s, 'w': road_connect_w }, 'weight': 1 },
        'neswew': { 'rules':  { 'n': road_connect_n, 'e': road_connect_e, 's': road_connect_s, 'w': road_connect_w }, 'weight': 0.5 },
        'neswns': { 'rules':  { 'n': road_connect_n, 'e': road_connect_e, 's': road_connect_s, 'w': road_connect_w }, 'weight': 0.5 },
        'ew': { 'rules':  { 'n': blank_connect_n, 'e': road_connect_e, 's': blank_connect_s, 'w': road_connect_w }, 'weight': 1 },
        'ns': { 'rules':  { 'n': road_connect_n, 'e': blank_connect_e, 's': road_connect_s, 'w': blank_connect_w }, 'weight': 1 },
        'none': { 'rules':  { 'n': blank_connect_n, 'e': blank_connect_e, 's': blank_connect_s, 'w': blank_connect_w }, 'weight': 1 },
        'nonea': { 'rules':  { 'n': blank_connect_n, 'e': blank_connect_e, 's': blank_connect_s, 'w': blank_connect_w }, 'weight': 0.25 },
        'noneb': { 'rules':  { 'n': blank_connect_n, 'e': blank_connect_e, 's': blank_connect_s, 'w': blank_connect_w }, 'weight': 0.25 },
        'se': { 'rules':  { 'n': road_connect_n, 'e': blank_connect_e, 's': blank_connect_s, 'w': road_connect_w }, 'weight': 1 },
        'sw': { 'rules':  { 'n': road_connect_n, 'e': road_connect_e, 's': blank_connect_s, 'w': blank_connect_w }, 'weight': 1 },
        'nw': { 'rules': { 'n': blank_connect_n, 'e': road_connect_e, 's': road_connect_s, 'w': blank_connect_w }, 'weight': 1 },
        'ne': { 'rules':  { 'n': blank_connect_n, 'e': blank_connect_e, 's': road_connect_s, 'w': road_connect_w }, 'weight': 1 },
        'new': { 'rules':  { 'n': blank_connect_n, 'e': road_connect_e, 's': road_connect_s, 'w': road_connect_w }, 'weight': 1 },
        'sew': { 'rules':  { 'n': road_connect_n, 'e': road_connect_e, 's': blank_connect_s, 'w': road_connect_w }, 'weight': 1 },
        'nes': { 'rules':  { 'n': road_connect_n, 'e': blank_connect_e, 's': road_connect_s, 'w': road_connect_w }, 'weight': 1 },
        'nws': { 'rules':  { 'n': road_connect_n, 'e': road_connect_e, 's': road_connect_s, 'w': blank_connect_w }, 'weight': 1 },
        'nhouse': { 'rules':  { 'n': blank_connect_n, 'e': blank_connect_e, 's': road_connect_s, 'w': blank_connect_w }, 'weight': 2 },
        'sea': { 'rules':  { 'n': ['nea'], 'e': blank_connect_e, 's': blank_connect_s, 'w': ['swa'] }, 'weight': 1 },
        'swa': { 'rules':  { 'n': ['nwa'], 'e': ['sea'], 's': blank_connect_s, 'w': blank_connect_w }, 'weight': 1 },
        'nwa': { 'rules':  { 'n': blank_connect_n, 'e': ['nea'], 's': ['swa'], 'w': blank_connect_w }, 'weight': 1 },
        'nea': { 'rules':  { 'n': blank_connect_n, 'e': blank_connect_e, 's': ['sea'], 'w': ['nwa'] }, 'weight': 1 },
        'nwall': { 'rules':  { 'n': blank_connect_n, 'e': blank_connect_e, 's': wall_connect_s, 'w': blank_connect_w }, 'weight': 0.25 },
        'ewall': { 'rules':  { 'n': blank_connect_n, 'e': blank_connect_e, 's': blank_connect_s, 'w': wall_connect_w }, 'weight': 0.25 },
        'swall': { 'rules':  { 'n': wall_connect_n, 'e': blank_connect_e, 's': blank_connect_s, 'w': blank_connect_w }, 'weight': 0.25 },
        'wwall': { 'rules':  { 'n': blank_connect_n, 'e': wall_connect_e, 's': blank_connect_s, 'w': blank_connect_w }, 'weight': 0.25 },
        'nswall': { 'rules':  { 'n': wall_connect_n, 'e': blank_connect_e, 's': wall_connect_s, 'w': blank_connect_w }, 'weight': 0.12 },
        'ewwall': { 'rules':  { 'n': blank_connect_n, 'e': wall_connect_e, 's': blank_connect_s, 'w': wall_connect_w }, 'weight': 0.12 }
    }
    t = solver.TileSet(tiles)
    s = solver.Solver(t, args.wrap)
    a = solver.App(s, args.delay, args.shownumbers, args.showchanged)
    a.on_execute()