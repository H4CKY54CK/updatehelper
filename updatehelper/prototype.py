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

cleanup = []

def bar(files):
    try:
        return tqdm(files, total=len(files))
    except Exception as e:
        return tqdm(files)

def update_emojis(args):
    path = 'temporary_emoji_folder'
    if os.path.exists(path):
        shutil.rmtree(path)
    shutil.copytree(args.source, path)
    paths = [path]
    files = []
    while paths:
        p = paths[0]
        for item in os.scandir(p):
            if item.is_dir():
                paths.append(item.path)
            elif item.name.lower().endswith('.png'):
                files.append(item.path)
        paths.pop(0)
    print("Resizing images...")
    for file in bar(files):
        with Image.open(file) as img:
            img = img.convert('RGBA')
            img = img.resize((40,40), Image.LANCZOS)
            img.save(file)
    print(f"Updating missing emojis in subreddit {subreddit.display_name}...")
    emojis = [i for i in subreddit.emoji]
    tba = []
    for file in os.scandir(path):
        if file.is_dir():
            for img in os.scandir(file.path):
                parent = os.path.basename(file.path)
                name = f"{parent}-{os.path.basename(img.path).replace('.png', '').replace('_4', '')}"
                loc = os.path.abspath(img.path)
                if any(name.startswith(str(i)) for i in range(8,15)) and name not in emojis:
                    tba.append((name,loc))
    for item in bar(tba):
        subreddit.emoji.add(item[0], item[1], post_flair_allowed=False)
        # print(f"Added {os.path.basename(loc)} as {name} in subreddit {subreddit.display_name}.") # interferes with tqdm
    cleanup.append(os.path.abspath(path))
    print("Emojis updated.")

def update_flairs(args):
    key = '3669320022109'
    print("Building spritesheets and stylesheet...")
    Sprite(args.source, 'sprites', 40, 40).start()
    sprites = 'sprites'
    spritesheets = []
    for item in os.scandir(sprites):
        if item.name.lower().endswith('.css'):
            stylesheet = os.path.abspath(os.path.join(sprites, 'stylesheet.css'))
        elif item.name.lower().endswith('.png'):
            spritesheets.append(os.path.abspath(item.path))
    # subreddit = reddit.subreddit(reddit.config.custom['subreddit'])
    for item in spritesheets:
        name = os.path.basename(item).replace('.png', '')
        subreddit.stylesheet.upload(name, item)
        print(f"Uploaded {os.path.basename(item)} as {name}")
    style = subreddit.stylesheet().stylesheet
    style = style.split(key)[0]
    style += f'{key}\n*/\n\n'
    with open(stylesheet) as f:
        data = f.read()
    style += data
    subreddit.stylesheet.update(style)
    print("Flairs updated.")
    cleanup.append(os.path.abspath(sprites))

def run_cleanup(files):
    print("Cleaning up...", end='\r')
    for item in files:
        try:
            shutil.rmtree(item)
        except:
            os.unlink(item)
    print("Cleanup finished.")

def run_all(args):
    update_emojis(args)
    update_flairs(args)

def run(args):
    print("Getting everything together...")
    global reddit, subreddit
    reddit = praw.Reddit('hackysack')
    subreddit = reddit.subreddit('flairtestingh4cky54ck')
    if args.task.lower() == 'all':
        run_all(args)
    else:
        TASKS[args.task.lower()](args)
    run_cleanup(cleanup)

def main(argv=None):
    argv = (argv or sys.argv)[1:]
    parser = argparse.ArgumentParser()
    parser.add_argument('task', type=str)
    parser.add_argument('source', type=str, nargs='?', default=None)
    parser.set_defaults(func=run)
    args = parser.parse_args(argv)
    args.func(args)

TASKS = {
    'emojis': update_emojis,
    'flairs': update_flairs,
}

if __name__ == '__main__':
    sys.exit(main())