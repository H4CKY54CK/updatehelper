import re
from setuptools import find_packages, setup
from codecs import open
from os import path
HERE = path.abspath(path.dirname(__file__))
PACKAGE_NAME = 'updatehelper'
with open(path.join(HERE, PACKAGE_NAME, "__init__.py"), encoding="utf-8") as fp:
    VERSION = re.search('__version__ = "([^"]+)"', fp.read()).group(1)

setup(name=PACKAGE_NAME,
      version=VERSION,
      description="Alpha Version",
      author='Hackysack',
      author_email='tk13xr37@gmail.com',
      packages=find_packages(exclude=[]),
      install_requires=['pillow', 'tqdm'],
      entry_points={'console_scripts':
          ['update = updatehelper.update:main']})
