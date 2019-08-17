# -*- coding: utf-8 -*-
"""
Created on Sat Aug 17 21:41:28 2019

@author: Dror
"""

import numpy as np

class Signal:
    sampleRate = None
    
    def realise(self, sampleRate):
        pass


class Sine(Signal):
    def __init__(self, frequency=220, duration=5000):
        self.frequency = frequency
        self.duration = duration
        
    def realise(self, sampleRate):
        return np.sin(self.frequency * np.linspace(0, self.duration, self.duration * sampleRate, False) * 2 * np.pi)
    
    
    
    
    