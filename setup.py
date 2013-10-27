#!/usr/bin/env python
from setuptools import setup, find_packages
from imago import __version__

setup(name='imago',
      version=__version__,
      packages=find_packages(),
      author="DataMade",
      author_email="info@datamade.us",
      license="MIT",
      url='http://github.com/datamade/chicago-elections/',
      description='Django backed API for Chicago Election Results',
      long_description='',
      platforms=['any'],
      install_requires=[
          'mongoengine==0.8.4',
          'Django<1.6',
          'BeautifulSoup',
          'scrapelib',
      ])
