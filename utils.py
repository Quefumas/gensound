# -*- coding: utf-8 -*-
"""
Created on Sat Aug 10 09:29:04 2019

@author: Dror
"""

import numpy as np

stretch = lambda buffer, bits: buffer * (2**(bits-1) - 1) / np.max(np.abs(buffer))

sin = lambda freq, seconds: np.sin(freq * np.linspace(0, seconds, seconds * sampleRate, False) * 2 * np.pi)

def fadeIn(buffer, seconds):
    global sampleRate
    amp = np.linspace(0, 1, seconds*sampleRate)
    # perhaps the fade in should be nonlinear
    buffer[0:seconds*sampleRate] = amp*buffer[0:seconds*sampleRate]

amp_freq = lambda buffer, freq, seconds, size: buffer* (sin(freq,seconds) * size + (1-size))