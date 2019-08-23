# -*- coding: utf-8 -*-
"""
Created on Sat Aug 17 21:41:28 2019

@author: Dror
"""

import numpy as np
from transforms import Transform, Amplitude
from utils import stretch
from audio import Audio

class Signal:
    def __init__(self):
        self.transforms = []
        self.total_duration = 0
        self.duration = 0
        # this is for processing purposes;
        # total_duration is when we add silence before/after, for efficiency
    
    #@abstractmethod ???
    def generate(self):
        """
        this is the part the generates the basic signal building block
        ####should return 2d np.ndarray
        should return 1d np.ndarray, the dims are fixed later...
        not sure if good
        TODO
        """
        pass
    
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
    
    def __radd__(self, other):
        assert(isinstance(other, Signal) or other == 0)
        
        if other == 0:
            return self
        
        if hasattr(self, "signals"):
            if hasattr(other, "signals"):
                self.signals.extend(other.signals)
                self.total_duration = max(self.total_duration, other.total_duration)
            else:
                self.signals.append(other)
                self.total_duration = max(self.total_duration, other.total_duration)
            return self
        else:
            if hasattr(other, "signals"):
                other.signals.append(self)
                other.total_duration = max(self.total_duration, other.total_duration)
                return other
            else:
                s = Signal()
                s.signals = [self, other]
                s.total_duration = max(self.total_duration, other.total_duration)
                return s
    
    def __add__(self, other):
        return other.__radd__(self)
    
    def realise(self, sample_rate):
        """ returns Audio instance.
        parses the entire signal tree recursively
        """
        self.sample_rate = sample_rate
        
        if not hasattr(self, "signals"):
            signal = self.generate()
            if len(signal.shape) == 1:
                signal.resize((1, signal.shape[0]))
                # TODO is this the place?
            audio = Audio(signal.shape[1], signal.shape[0], sample_rate)
            audio.from_array(signal, self.sample_rate)
        else:
            audio = Audio(self.total_duration * self.sample_rate, 1, sample_rate)
            
            for signal in self.signals:
                audio += signal.realise(self.sample_rate)
        
        for transform in self.transforms:
            transform.realise(signal=self, audio=audio)
            
        return audio
    
    def mixdown(self, sample_rate=11025, byte_width=2):
        self.sample_rate = sample_rate        
        self.audio = self.realise(sample_rate)
        return self.audio.mixdown(byte_width)

class Sine(Signal):
    def __init__(self, frequency=220, duration=5):
        super().__init__()
        self.frequency = frequency
        self.duration = duration
        self.total_duration = duration # because of Shift. is there a better way?
        
    def generate(self):
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
        return (((2*np.pi* self.frequency * np.linspace(0, self.duration, self.duration * self.sample_rate, False) % (2*np.pi)) < np.pi) - np.pi).astype(np.float64)

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
    
    
    
    
    