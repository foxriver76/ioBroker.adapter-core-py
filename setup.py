#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr 14 11:09:30 2020

@author: moritz
"""

import setuptools

setuptools.setup(name='iobroker.adapter-core-py',
      version='0.1.0',
      description='Python Controller for ioBroker adapters',
      url='https://github.com/foxriver76',
      author='Moritz Heusinger',
      author_email='moritz.heusinger@gmail.com',
      packages=setuptools.find_packages(),
      install_requires=[
              'aioredis'
      ],
      license='CC-BY-NC-4.0',
      zip_safe=False)