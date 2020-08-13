import argparse
import sys

def run(args):
    if args.first:
        print(args.first)
    else:
        print("You didn't enter anything.")

def main(argv=None):
    argv = (argv or sys.argv)[1:]
    parser = argparse.ArgumentParser()
    parser.add_argument('first', type=str, nargs='?', default=None)
    parser.set_defaults(func=run)
    args = parser.parse_args(argv)
    args.func(args)

if __name__ == '__main__':
    sys.exit(main())