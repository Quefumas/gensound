# -*- coding: utf-8 -*-
"""
Created on Sat Aug 10 09:24:24 2019

@author: Dror
"""

import numpy as np

midA = 440
octave = 2

semitone = np.power(octave, 1/12)
cent = np.power(semitone, 1/100)

midC = lambda s: midA*semitone**(-9+s)