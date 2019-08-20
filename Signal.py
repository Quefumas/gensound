# -*- coding: utf-8 -*-
"""
Created on Sat Aug 17 21:41:28 2019

@author: Dror
"""

import numpy as np
from transforms import Transform, Amplitude

class Signal:
    def __init__(self):
        self.transforms = []
    
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
        transform.on_apply(self)
    
    def __rmul__(self, other):
        assert(type(other) is float)
        assert(-1 <= other <= 1)
        
        self.apply(Amplitude(size = other))
        return self
    
    def __mul__(self, other):
        assert(isinstance(other, Transform))
        self.apply(other)
        return self


class Sine(Signal):
    def __init__(self, frequency=220, duration=5):
        super().__init__()
        self.frequency = frequency
        self.duration = duration
        self.total_duration = duration # because of Shift. is there a better way?
        
    def generate(self):
        #self.length = self.duration * self.sample_rate
        return np.sin(self.frequency * np.linspace(0, self.duration, self.duration * self.sample_rate, False) * 2 * np.pi)
    
class Triangle(Signal):
    def __init__(self, frequency=220, duration=5):
        super().__init__()
        self.frequency = frequency
        self.duration = duration
        self.total_duration = duration # put this into a superclass of sine and triangle?
    
    def generate(self):
        # strange manipulation on sawtooth
        return 2*np.abs((2*np.pi* self.frequency * np.linspace(0, self.duration, self.duration * self.sample_rate, False) % (2*np.pi))-np.pi)-np.pi
    
    
class Square(Signal):
    def __init__(self, frequency=220, duration=5):
        super().__init__()
        self.frequency = frequency
        self.duration = duration
        self.total_duration = duration
    
    def generate(self):
        return ((2*np.pi* self.frequency * np.linspace(0, self.duration, self.duration * self.sample_rate, False) % (2*np.pi)) < np.pi).astype(np.float64)

class Sawtooth(Signal):
    def __init__(self, frequency=220, duration=5):
        super().__init__()
        self.frequency = frequency
        self.duration = duration
        self.total_duration = duration
    
    def generate(self):
        return (2*np.pi* self.frequency * np.linspace(0, self.duration, self.duration * self.sample_rate, False) % (2*np.pi))-np.pi

class GreyNoise(Signal):
    def __init__(self, duration=5):
        super().__init__()
        self.duration = duration
        self.total_duration = duration
    
    def generate(self):
        return 2*np.random.rand(self.duration*self.sample_rate) - 1
    
    
    
    
    