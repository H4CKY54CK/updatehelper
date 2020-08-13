import os
import sys
import shutil
import argparse
from math import sqrt, ceil, floor
from PIL import Image
from threading import Thread

class Sprite:

    def __init__(self, source, output, width, height):

        self.source = [source]
        self.dirs = []
        while self.source:
            path = self.source[0]
            for item in os.scandir(path):
                if item.is_dir():
                    self.source.append(item.path)
                    self.dirs.append(item.path)
            self.source.pop(0)
        if not self.dirs:
            self.dirs = [source]
        self.width = width
        self.height = height
        self.output = output
        if os.path.exists(self.output):
            shutil.rmtree(self.output)
        os.mkdir(self.output)

    def start(self):

        p = None
        if len(self.dirs) > 1:
            p = True
        threads = []
        for item in self.dirs:
            t1 = Thread(target=self.single_sheet, args=(item, self.width, self.height, self.output))
            t2 = Thread(target=self.generate_stylesheet, args=(item, self.width, self.height, self.output), kwargs={'project': p})
            threads.extend((t1,t2))
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

    def single_sheet(self, source, width, height, output):
        
        images = [file.path for file in os.scandir(source)]
        if len(images) > ceil(sqrt(len(images))) * floor(sqrt(len(images))):
            rows, cols = ceil(sqrt(len(images))), ceil(sqrt(len(images)))
        else:
            rows, cols = ceil(sqrt(len(images))), floor(sqrt(len(images)))
        size = Image.open(images[0]).size
        canvas = (size[0]*rows,size[1]*cols)
        x = y = 0
        sheet = Image.new('RGBA', canvas)
        for item in images:
            if os.path.isdir(item):
                continue
            sheet.paste(Image.open(item), (x,y))
            x += size[0]
            if x >= canvas[0]:
                x = 0
                y += size[1]
        if width and height:
            sheet = sheet.resize((width*rows, height*cols), Image.LANCZOS)
        # if not os.path.exists(output):
            # os.mkdir(output)
        filename = os.path.join(output, 'flairs-{}.png'.format(os.path.split(source)[1]))
        sheet.save(filename,'PNG')
    
    def generate_stylesheet(self, source, width, height, output, project=None):

        images = [file for file in os.scandir(source)]
        size = Image.open(images[0].path).size
        if width and height:
            size = (width,height)
        x = y = 0
        if len(images) > ceil(sqrt(len(images))) * floor(sqrt(len(images))):
            rows, cols = ceil(sqrt(len(images))), ceil(sqrt(len(images)))
        else:
            rows, cols = ceil(sqrt(len(images))), floor(sqrt(len(images)))
        stylesheet = os.path.join(output,'stylesheet.css')
        lines = []
        folder = ''
        if project:
            folder = os.path.split(os.path.dirname(images[0].path))[1] + '-'
            line = f'\n.flair[class*="{folder[:-1]}-"] {{background-image: url(%%flairs-{folder[:-1]}%%);}}\n\n'
            lines.append(line)
        for item in images:
            if os.path.isdir(item):
                continue
            line = f".flair-{folder}{item.name.replace('.png', '').replace('_4', '')} {{min-width: {size[0]}px; background-position: {'-' if x != 0 else ''}{x}{'px' if x != 0 else ''} {'-' if y != 0 else ''}{y}{'px' if y != 0 else ''};}}\n"
            x += size[0]
            if x >= size[0] * rows:
                x = 0
                y += size[1]
            lines.append(line)
        with open(stylesheet, 'a') as f:
            f.writelines(lines)
