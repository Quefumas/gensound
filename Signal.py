# -*- coding: utf-8 -*-
"""
Created on Sat Aug 17 21:41:28 2019

@author: Dror
"""

import numpy as np

from transforms import Transform, Amplitude
from audio import Audio
from playback import WAV_to_Audio

class Signal:
    def __init__(self):
        self.transforms = []
    
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
    
    def __rmul__(self, other):
        assert(type(other) in (float, int))
        #other = float(other)
        # TODO why this assertion? what's wrong with greater values?
        #assert(-1 <= other <= 1)
        
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
            else:
                self.signals.append(other)
            return self
        else:
            if hasattr(other, "signals"):
                other.signals.append(self)
                return other
            else:
                s = Signal()
                s.signals = [self, other]
                return s
    
    def __add__(self, other):
        return other.__radd__(self)
    
    def __sub__(self, other):
        return self.__add__(-1.0*other)
    
    def __neg__(self):
        return -1.0*self
    
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
            audio = Audio(signal.shape[0], sample_rate)
            audio.from_array(signal)
        else:
            audio = Audio(1, sample_rate)
            
            for signal in self.signals:
                audio += signal.realise(self.sample_rate)
        
        for transform in self.transforms:
            transform.realise(signal=self, audio=audio)
            
        return audio
    
    def mixdown(self, sample_rate, byte_width, max_amplitude=1):
        """
        0 < max_amplitude <= 1 implies stretching the amplitudes
        so they would hit absolute value of max_amplitude.
        otherwise, max_amplitude = None implies not to touch the amplitudes
        as given, unless they exceed 1 in which case we shrink everything proportionally.
        """
        # TODO does this need num channels?
        self.sample_rate = sample_rate        
        self.audio = self.realise(sample_rate)
        return self.audio.mixdown(byte_width, max_amplitude)

#### particular signals

class Silence(Signal):
    def __init__(self, duration=5000):
        super().__init__()
        self.duration = duration
    
    def generate(self):
        return np.zeros(self.duration, dtype=np.float64)

class Sine(Signal):
    def __init__(self, frequency=220, duration=5000):
        super().__init__()
        self.frequency = frequency
        self.duration = duration
        
    def generate(self):
        return np.sin(self.frequency * np.linspace(0, self.duration/1000, int(self.duration * self.sample_rate/1000), False) * 2 * np.pi)
    
class Triangle(Signal):
    def __init__(self, frequency=220, duration=5000):
        super().__init__()
        self.frequency = frequency
        self.duration = duration
    
    def generate(self):
        # strange manipulation on sawtooth
        return 2*np.abs((2*np.pi* self.frequency * np.linspace(0, self.duration/1000, int(self.duration * self.sample_rate/1000), False) % (2*np.pi))-np.pi)-np.pi
    
    
class Square(Signal):
    def __init__(self, frequency=220, duration=5000):
        super().__init__()
        self.frequency = frequency
        self.duration = duration
    
    def generate(self):
        return (((2*np.pi* self.frequency * np.linspace(0, self.duration/1000, int(self.duration * self.sample_rate/1000), False) % (2*np.pi)) < np.pi) - np.pi).astype(np.float64)

class Sawtooth(Signal):
    def __init__(self, frequency=220, duration=5000):
        super().__init__()
        self.frequency = frequency
        self.duration = duration
    
    def generate(self):
        return (2*np.pi* self.frequency * np.linspace(0, self.duration/1000, int(self.duration * self.sample_rate/1000), False) % (2*np.pi))-np.pi

class Step(Signal):
    def __init__(self, duration=1):
        super().__init__()
        self.duration = duration
    
    def generate(self):
        return np.ones((int(self.duration*self.sample_rate/1000),), dtype=np.float64)

class GreyNoise(Signal):
    def __init__(self, duration=5000):
        super().__init__()
        self.duration = duration
    
    def generate(self):
        return 2*np.random.rand(int(self.duration*self.sample_rate/1000)) - 1



### raw audio signals

class Raw(Signal):
    """
    Keep track of when the audio is copied;
    we should probably use a view until we start applying transforms.
    I.e. this object should only keep a view, and on generate it should copy.
    """
    def __init__(self, audio):
        super().__init__()
        self.audio = audio
    
    def generate(self):
        #return np.copy(self.audio.audio)
        return self.audio.audio
    """
    TODO
    ####think about this more. here we're copying the audio data,
    #### but not the audio object. should we copy the audio object instead maybe?
    we're passing the direct audio buffer.
    since this eventually goes to audio.from_Array, in which np.copy is called,
    this SHOULD not cause problems when using the same shell for different copies
    of the same original signal.
    """


class WAV(Raw):
    cache = {}
    
    def __init__(self, filename):
        if filename in WAV.cache:
            audio = WAV.cache[filename].copy()
        else:
            audio = WAV_to_Audio(filename)
            WAV.cache[filename] = audio
        
        # TODO copy again? so the cache will be eternally independent?
        super().__init__(audio)
    






















