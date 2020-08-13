from urllib.request import urlopen
import sys
import argparse
import shutil
import os
from PIL import Image
from tqdm import tqdm
import json
import subprocess
import praw
from misctools import __version__ as miscversion

EXC2 = [
    'back_circle.png',
    'cadre.png',
    'cadre_hover.png',
    'cc-left.png',
    'cc-right.png',
    'favicon.png',
    'main_white_pur.png',
    'no_img.png',
    ]
EXCLUDED = [
    '14003.png',
    '194001.png',
    'no_image.png',
    '8084001.png',
    '8164002.png',
    '8104001.png',
    '8083001.png',
    '8061001.png',
    '8164001.png',
    '8063001.png',
    '8014001.png',
    '8464001.png',
    '8062001.png',
    '65032.png',
    '8364001.png',
    '8264001.png',
    ]

images = 'images'
ddirs = {'1':'one', '2':'two', '3':'three', '4':'four', '5':'five', '6':'six', '7':'seven', '8':'eight', '9':'nine'}

def sort_by_rarity(source):
    print("Sorting by rarity...")
    for item in tqdm(os.scandir(source), total=len(os.listdir(source))):
        if item.name in EXC2:
            continue
        part = item.name.rstrip('.png')
        if part.endswith('_4'):
            part = part.split('_4')[0]
        part = part[::-1]
        rarity = part[3]
        rarity = ddirs[rarity]
        if not os.path.exists(rarity):
            os.mkdir(rarity)
        output = os.path.join(os.getcwd(), rarity, item.name)
        shutil.copy(item.path, output)
        if rarity == 'six':
            if item.name.endswith('_4.png'):
                path, thing = os.path.split(output)
                output = os.path.join(path, 'mlb')
                if not os.path.exists(output):
                    os.mkdir(output)
                output = os.path.join(output, item.name)
                shutil.copy(item.path, output)
            else:
                path, thing = os.path.split(output)
                output = os.path.join(path, 'reg')
                if not os.path.exists(output):
                    os.mkdir(output)
                output = os.path.join(output, item.name)
                shutil.copy(item.path, output)
    print("Done.")

def template(folder):
    page = []
    for i in os.listdir(folder):
        img = f"./images/{i}"
        flair = i.split('.png')[0]
        cadre = "./assets/cadre.png"
        cadre_hover = "./assets/cadre_hover.png"
        template = f"""
                        <span class="glob__img-character-list" onclick="majSrc('{flair}')">
                            <img src="{img}" class="thum_character-list" alt="avatar" onerror="this.onerror=null;this.src='./assets/no_img.png';">
                        </span>"""
        page.append(template)
    return page

dirs = [
    'newest',
    r'six\mlb',
    r'six\reg',
    'five',
    'four',
    'three',
    'two',
    'one'
]

headers = (i for i in ['Newest', 'Max Limit Break', 'Six Stars', 'Five Stars', 'Four Stars', 'Three Stars', 'Two Stars', 'One Star'])

def start():
    sort_by_rarity(images)
    with open('page.txt', 'w') as f:
        for item in dirs:
            f.write(f"""\n
                        <h1>{next(headers)}</h1>
    """)
            page = template(item)
            f.write('\n'.join(page))


def update(args=None):
    if miscversion != '2.0.1':
        subprocess.run('pip install https://github.com/h4cky54ck/misctools/archive/master.zip')
        if subprocess.getoutput('spriteit -V') != 'v2.0.1':
            print("The automatic install feature has failed. Please upgrade your `misctools` package via `pip install https://github.com/h4cky54ck/misctools/archive/master.zip`")
            sys.exit()

    if not os.path.exists('256'):
        print("Folder `256` not in current directory... Searching user's folder...")
        shared = os.path.join(os.path.expanduser('~'), 'Nox_share', 'ImageShare', '256')
        if os.path.exists(shared):
            print("Copying folder to current directory...")
            shutil.copytree(shared, '256')
            print("Fetching `CCZ_Decrypter.exe`...")
            decrypter = 'CCZ_Decrypter.exe'
            if os.path.exists(decrypter):
                rd = os.path.abspath(decrypter)
                print("Found decrypter.")
            else:
                found = False
                for root, dirs, files in os.walk(os.path.expanduser('~')):
                    for f in files:
                        if f == decrypter:
                            print("Found decrypter.")
                            rd = os.path.join(root, f)
                            found = True
                            break
                    if found:
                        break
            print("Decrypting files...")
            subprocess.run(f"{rd} 256")
            print("Done. Continuing...")
    update_init()
    current = os.getcwd()
    dest = os.path.join(os.path.expanduser('~'), 'Documents', 'Github', 'flair-selector')
    mergefolders(current, dest)
    print("Folders merged")
    uh = "https://github.com/H4CKY54CK/updatehelper/archive/master.zip"
    wgetit(uh, 'updatehelper.zip')
    unarchit('updatehelper.zip')
    shutil.copytree(os.path.join(current, 'updatehelper', 'updatehelper-master', 'flairs'), 'flairs')
    nine = os.path.join(current, 'flairs', '9')
    ten = os.path.join(current, 'flairs', '10')
    imgs = []
    for item in os.scandir('flairs'):
        if item.is_dir():
            for img in os.scandir(item.path):
                imgs.append(img.name)
    for item in os.scandir('256'):
        if item.name not in imgs and item.name not in EXCLUDED:
            if item.name.endswith('_4.png'):
                shutil.copy(item.path, os.path.join(ten, item.name))
            else:
                shutil.copy(item.path, os.path.join(nine, item.name))

    subprocess.run('spriteit flairs -x 40 -y 40')
    global reddit, subreddit
    reddit = praw.Reddit('default')
    subreddit = reddit.subreddit(reddit.config.custom['subreddit'])
    for item in os.scandir('sprites'):
        if item.name.endswith('.png'):
            subreddit.stylesheet.upload(item.name.replace('.png', ''), item.path)
            print(f"Uploaded {item.name} as {item.name.replace('.png', '')} in {subreddit.display_name}.")
    style = os.path.join('sprites', 'stylesheet.css')
    with open(style) as f:
        data = f.read()
    subreddit.stylesheet.update(data)
    print(f"Updated stylesheet in {subreddit.display_name}.")
    update_bot()
    update_emojis()

def update_emojis():
    path = 'temporary_emoji_folder'
    if os.path.exists(path):
        shutil.rmtree(path)
    shutil.copytree('flairs', path)
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
    for file in tqdm(files):
        with Image.open(file) as img:
            img = img.convert('RGBA')
            img = img.resize((40,40), Image.LANCZOS)
            img.save(file)
    print(f"Updating missing emojis in the subreddit {subreddit.display_name}...")
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
    for item in tqdm(tba):
        subreddit.emoji.add(item[0], item[1], post_flair_allowed=False)
    print("Cleaning up...")
    if os.path.exists(path):
        shutil.rmtree(path)
    print("Emojis have been updated.")

def mergefolders(root_src_dir, root_dst_dir):
    for src_dir, dirs, files in os.walk(root_src_dir):
        dst_dir = src_dir.replace(root_src_dir, root_dst_dir, 1)
        if not os.path.exists(dst_dir):
            os.makedirs(dst_dir)
        for file_ in files:
            src_file = os.path.join(src_dir, file_)
            dst_file = os.path.join(dst_dir, file_)
            if os.path.exists(dst_file):
                os.remove(dst_file)
            shutil.copy(src_file, dst_dir)

def update_init():
    url = "https://github.com/H4CKY54CK/flair-selector/archive/master.zip"
    wgetit(url, 'flairstuffs.zip')
    unarchit('flairstuffs.zip')
    images = r"flairstuffs\flair-selector-master\images"
    if os.path.exists('images'):
        shutil.rmtree('images')
    shutil.move(images, 'images')
    for item in os.scandir('256'):
        name = item.name.replace('thumbnail_', '')
        path = os.path.join(os.path.split(item.path)[0], name)
        os.rename(item.path, path)
    a = set(os.listdir('256'))
    b = set(os.listdir('images'))
    c = set(EXCLUDED)
    d = a - (b | c)
    e = []
    for item in d:
        e.append(r'256\{}'.format(item))
    if not os.path.exists('newest'):
        os.mkdir('newest')
    for item in e:
        name = os.path.split(item)[1]
        path = r'newest\{}'.format(name)
        shutil.copy(item, path)
    if os.path.exists('assets'):
        shutil.rmtree('assets')
    shutil.copytree(r"flairstuffs\flair-selector-master\assets", 'assets')
    for item in os.scandir('newest'):
        img = Image.open(item.path)
        img = img.convert('RGBA')
        img = img.resize((80,80), Image.LANCZOS)
        img.save(os.path.join('images', item.name))
        img = img.resize((60,60), Image.LANCZOS)
        img.save(os.path.join('assets', item.name))
    start()
    with open('index.html', 'wb') as f:
        f.write(urlopen('https://raw.githubusercontent.com/H4CKY54CK/flair-selector/master/index.html').read())
    update_html()
    for item in dirs:
        shutil.rmtree(item)
    shutil.rmtree('six')
    os.remove('page.txt')
    shutil.rmtree('flairstuffs')


def update_bot():
    data = json.load(urlopen("https://raw.githubusercontent.com/H4CKY54CK/flair-selector/master/flairs.json"))
    uh = 'updatehelper'
    images = os.path.join('flairs')
    d = {}
    for folder in os.scandir(images):
        for image in os.scandir(folder.path):
            k = f"{image.name.replace('.png','')}"
            v = f"{folder.name}-{image.name.replace('.png','').replace('_4','').replace('_1','')}"
            d.update({k:v})
    json.dump(d, open('f.json','w'),indent=4)
    current = os.getcwd()
    dest = os.path.join(os.path.expanduser('~'), 'Documents', 'Github', 'flair-selector')
    shutil.copy('f.json',os.path.join(dest,'flairs.json'))
    os.chdir(dest)
    os.system('git add .')
    os.system('git commit -m "update"')
    os.system('git push origin master')
    os.chdir(current)





def update_html():
    key1 = """                    <!-- -->
                        </div>"""
    key2 = """                        </span>
                    </div>
                </div>
            </div>
        </div>"""
    with open('index.html') as f:
        data = f.read()
    data1 = data.split(key1)[0]
    data3 = data.split(key2)[1]
    with open('page.txt') as f:
        data2 = f.read()
    complete = data1 + key1 + '\n' + data2 + key2 + data3
    with open('index.html', 'w') as f:
        f.write(complete)
    print("HTML file written.")

def unarchit(source, output=None):

    source = os.path.abspath(source)
    base, suffix = os.path.splitext(source)
    if suffix.lower() in ['.gz', '.bz2', '.xz']:
        base, second = os.path.splitext(base)
        suffix = second + '.' + suffix.strip('.2')

    output = str(source).split(suffix)[0] if not output else output

    shutil.unpack_archive(source, output)
    print('Finished extracting.')
    os.remove(source)

def wgetit(url, name):
    try:
        with open(name, 'wb') as f:
            f.write(urlopen(url).read())
            return f"{url} -> {name}"
    except Exception as e:
        return str(e)

def main(argv=None):
    argv = (argv or sys.argv)[1:]
    parser = argparse.ArgumentParser()
    parser.set_defaults(func=update)
    args = parser.parse_args(argv)
    args.func(args)

if __name__ == '__main__':
    sys.exit(main())