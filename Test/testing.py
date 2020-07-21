# -*- coding: utf-8 -*-
"""
Created on Mon Jul 13 19:20:15 2020

@author: 12699
"""

from pyfixorchestra import FixDictionary

test = FixDictionary("components")
asd = (test.generateDictionary())

print((asd.keys()))
