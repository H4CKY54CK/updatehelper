import argparse
import time
import sys
import os
import praw
import json
import shutil
import subprocess
from PIL import Image
from tqdm import tqdm
from math import sqrt, ceil, floor
from threading import Thread
from .sprite import Sprite
from .exclude import exclude

def run_updates(args=None):
    home = os.path.abspath('256')
    if not os.path.exists(home):
        shared = os.path.join(os.path.expanduser('~'), 'Nox_share', 'ImageShare', '256')
        if os.path.exists(shared):
            shutil.copytree(shared, home)

def main(argv=None):
    argv = (argv or sys.argv)[1:]
    parser = argparse.ArgumentParser()
    parser.add_argument('task', type=str)
    parser.set_defaults(func=run_updates)
    args = parser.parse_args(argv)
    args.func(args)

if __name__ == '__main__':
    sys.exit(main())