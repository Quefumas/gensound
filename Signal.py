# -*- coding: utf-8 -*-
"""
Created on Sat Aug 17 21:41:28 2019

@author: Dror
"""

import numpy as np

class Signal:
    def generate(self):
        pass
    
    def realise(self, sample_rate):
        self.sample_rate = sample_rate
        audio = self.generate()
        
        for transform in self.transforms:
            transform.realise(signal=self, audio=audio)
            
        return audio
    
    # TODO maybe use += instead???
    # TODO maybe use *= instead, and += to mix stuff together???
    # then we can use * also to advance stuff forward
    def apply(self, transform):
        
        self.transforms.append(transform)


class Sine(Signal):
    def __init__(self, frequency=220, duration=5):
        self.transforms = []
        self.frequency = frequency
        self.duration = duration
        
    def generate(self):
        self.length = self.duration * self.sample_rate
        return np.sin(self.frequency * np.linspace(0, self.duration, self.duration * self.sample_rate, False) * 2 * np.pi)
    
    
    
    
    