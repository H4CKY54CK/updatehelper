from urllib.request import urlopen
import sys
import argparse
import shutil
import os
from PIL import Image
from tqdm import tqdm
import json

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
    if args.task == 'all':
        update_init()
    update_bot()
    current = os.path.dirname(os.getcwd())
    dest = os.path.join(os.path.expanduser('~'), 'Documents', 'Github', 'flair-selector')
    mergefolders(current, dest)
    print("Folders merged")
    os.chdir(dest)
    os.system('git add .')
    os.system('git commit -m "update"')
    os.system('git push origin master')


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
    uh = "https://github.com/H4CKY54CK/updatehelper/archive/master.zip"
    wgetit(uh, 'updatehelper.zip')
    unarchit('updatehelper.zip')
    uh = 'updatehelper'
    images = os.path.join(uh, 'flairs')
    d = {}
    for folder in os.scandir(images):
        for image in os.scandir(folder.path):
            k = f"{image.name.replace('.png','').replace('_4','')}"
            v = f"{folder.name}-{image.name.replace('.png','').replace('_4','')}"
            d.update({k:v})
    json.dump(d, open('f.json','w'),indent=4)
    current = os.path.dirname(os.getcwd())
    dest = os.path.join(os.path.expanduser('~'), 'Documents', 'Github', 'reddit-flair-bot')
    mergefolders(current,dest)
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
    parser.add_argument('task', type=str)
    parser.set_defaults(func=update)
    args = parser.parse_args(argv)
    args.func(args)

if __name__ == '__main__':
    sys.exit(main())