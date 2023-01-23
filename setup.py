# -*- coding: utf-8 -*-

# versions
import codecs
import os
from pathlib import Path
import setuptools
__version__ = os.environ.get('VERSION_NEW', '0.9.0')

# requirements
try:
  with open('requirements.txt') as f:
    reqs = f.read().splitlines()
except FileNotFoundError:
  reqs = []

# description
with codecs.open("README.md", "r", encoding="UTF-8") as fh:
  long_description = fh.read()

setuptools.setup(
  name = 'tool_json_writer',
  version = __version__,
  author = u'Martin Beneš',
  author_email = 'martinbenes1996@gmail.com',
  description = 'JSON Writer for an Uncover tool.',
  long_description = long_description,
  long_description_content_type="text/markdown",
  packages=setuptools.find_packages(),
  license='MIT',
  url = {
    "Source": 'https://github.com/uibk-uncover/tool_json_writer',
  },
  keywords = ['json','format','output','compatibility'],
  install_requires=reqs,
  package_dir={'': '.'},
  classifiers=[
    'Development Status :: 2 - Pre-Alpha',
    'Intended Audience :: Science/Research',
    'Intended Audience :: Developers',
    'Intended Audience :: Information Technology',
    'Intended Audience :: Legal Industry',
    'Intended Audience :: Other Audience',
    'License :: OSI Approved :: MIT License',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Programming Language :: Python :: 3',
    'Topic :: Communications',
    'Topic :: Scientific/Engineering',
    'Topic :: Scientific/Engineering :: Image Processing',
    'Topic :: Scientific/Engineering :: Information Analysis',
    'Topic :: Software Development :: Libraries',
    'Topic :: Software Development :: Libraries :: Python Modules',
    'Topic :: Utilities'
  ],
)

