import re
from setuptools import find_packages, setup
from codecs import open
import os
HERE = os.path.abspath(os.path.dirname(__file__))
PACKAGE_NAME = 'updatehelper'
with open(os.path.join(HERE, PACKAGE_NAME, "__init__.py"), encoding="utf-8") as fp:
    VERSION = re.search('__version__ = "([^"]+)"', fp.read()).group(1)

setup(name=PACKAGE_NAME,
      version=VERSION,
      description="This tool is intended for the subreddit /r/MemoryDefrag.",
      author='Hackysack',
      author_email='h4cky54ck@gmail.com',
      packages=find_packages(exclude=[]),
      install_requires=['pillow', 'tqdm'],
      entry_points={'console_scripts':
          ['update = updatehelper.update:main',
           'test = updatehelper.prototype:main',
            ]})
