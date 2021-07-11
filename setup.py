# -*- coding: utf-8 -*-

from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(name='gensound',
      version='0.5',
      author='Dror Chawin',
      author_email='quefumas@gmail.com',
      description='Pythonic audio processing and synthesis library',
      packages=['gensound'],
      long_description=long_description,
      long_description_content_type='text/markdown',
      url='https://github.com/Quefumas/gensound',
      install_requires=['numpy'],
      package_data={'gensound': ['data/Kushaura_sketch.wav']},
      )