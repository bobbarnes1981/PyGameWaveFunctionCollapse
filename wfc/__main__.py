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
    parser.add_argument('-l', '--logging', type=str, required=False, default='INFO', dest='logging', choices=loglevels)
    args = parser.parse_args()
    
    loglevel = getattr(logging, args.logging, None)
    logging.basicConfig(level=loglevel, format='%(asctime)s %(levelname)s %(name)s %(message)s')

    a = solver.App(args.delay)
    a.on_execute()