# -*- coding: utf-8 -*-
"""
Created on Sat Aug 17 21:41:28 2019

@author: Dror
"""

import copy

import numpy as np

from transforms import Transform, Amplitude
from audio import Audio
from playback import WAV_to_Audio
from utils import is_number

class Signal:
    def __init__(self):
        self.transforms = []
    
    #@abstractmethod ???
    def generate(self, sample_rate):
        """
        this is the part the generates the basic signal building block
        ####should return 2d np.ndarray
        should return 1d np.ndarray, the dims are fixed later...
        not sure if good
        TODO
        """
        pass
    
    def copy(self):
        """
        creates an identical signal object.
        """
        return copy.deepcopy(self)
    
    @staticmethod
    def concat(*args):
        s = Signal()
        s.sequence = args
        return s
    
    def realise(self, sample_rate):
        """ returns Audio instance.
        parses the entire signal tree recursively
        """
        assert not (hasattr(self, "sequence") and hasattr(self, "signals"))
        
        if hasattr(self, "sequence"):
            audio = Audio(sample_rate)
            for signal in self.sequence:
                audio.append(signal.realise(sample_rate))
        elif not hasattr(self, "signals"): # leaf of the mix tree
            signal = self.generate(sample_rate)
            if len(signal.shape) == 1:
                signal.resize((1, signal.shape[0]))
                # TODO is this the place?
            audio = Audio(sample_rate)
            audio.from_array(signal)
        else: # internal node
            audio = Audio(sample_rate)
            
            for signal in self.signals:
                audio += signal.realise(sample_rate)
        
        for transform in self.transforms:
            transform.realise(audio=audio)
            
        return audio
    
    def mixdown(self, sample_rate, byte_width, max_amplitude=1):
        """
        0 < max_amplitude <= 1 implies stretching the amplitudes
        so they would hit absolute value of max_amplitude.
        otherwise, max_amplitude = None implies not to touch the amplitudes
        as given, unless they exceed 1 in which case we shrink everything proportionally.
        """
        # TODO does this need num channels?
        # perhaps some signals are inherently multiple-channeled?
        audio = self.realise(sample_rate)
        return audio.mixdown(byte_width, max_amplitude)
    
    ########################
    
    def __str__(self):
        if hasattr(self, "sequence"):
            res = "[{}]".format(" + ".join([str(signal) for signal in self.sequence]))
        elif not hasattr(self, "signals"):
            res = str(type(self).__name__)
        else:
            res = "({})".format(" + ".join([str(signal) for signal in self.signals]))
        res += "" if len(self.transforms) == 0 else "*({})".format(",".join([str(transform) for transform in self.transforms]))
        return res
    
    def __pow__(self, other):
        assert type(other) == int
        return Signal.concat(*[self]*other)
    
    def __rmul__(self, other):
        """ multiplication from the left is only legal for numbers, not for transforms"""
        assert is_number(other)
        return self*Amplitude(size = other)
    
    def __mul__(self, other):
        """
        signals can be multiplied on the right by both floats and transforms
        """
        if not isinstance(other, Transform):
            return self.__rmul__(other)
        s = self.copy()
        s.transforms.append(other)
        return s
    
    def __radd__(self, other):
        if other == 0:
            return self
        
        raise TypeError("Signal can only be added to other signals, or to 0.")
    
    def __add__(self, other):
        """
        create empty signal list.
        for each operand, if it is transformed or a single signal,
        append it to the list.
        otherwise, it is an untransformed list, simply extend the signal list.
        """
        s = Signal()
        s.signals = []
        
        if len(self.transforms) == 0 and hasattr(self, "signals"):
            s.signals += self.signals
        else:
            s.signals += [self]
        
        if len(other.transforms) == 0 and hasattr(other, "signals"):
            s.signals += other.signals
        else:
            s.signals += [other]
        
        return s
    
    def __sub__(self, other):
        return self.__add__(-1.0*other)
    
    def __neg__(self):
        return -1.0*self
    
    

#### particular signals

class Silence(Signal):
    def __init__(self, duration=5000):
        super().__init__()
        self.duration = duration
        # TODO appears to be wrong duration, should take into account sample rate
    
    def generate(self, sample_rate):
        return np.zeros(self.duration, dtype=np.float64)

class Sine(Signal):
    def __init__(self, frequency=220, duration=5000):
        super().__init__()
        self.frequency = frequency
        self.duration = duration
        
    def generate(self, sample_rate):
        return np.sin(self.frequency * np.linspace(0, self.duration/1000, int(self.duration * sample_rate/1000), False) * 2 * np.pi)
    
class Triangle(Signal):
    def __init__(self, frequency=220, duration=5000):
        super().__init__()
        self.frequency = frequency
        self.duration = duration
    
    def generate(self, sample_rate):
        # strange manipulation on sawtooth
        return 2*np.abs((2*np.pi* self.frequency * np.linspace(0, self.duration/1000, int(self.duration * sample_rate/1000), False) % (2*np.pi))-np.pi)-np.pi
    
    
class Square(Signal):
    def __init__(self, frequency=220, duration=5000):
        super().__init__()
        self.frequency = frequency
        self.duration = duration
    
    def generate(self, sample_rate):
        return (((2*np.pi* self.frequency * np.linspace(0, self.duration/1000, int(self.duration * sample_rate/1000), False) % (2*np.pi)) < np.pi) - np.pi).astype(np.float64)

class Sawtooth(Signal):
    def __init__(self, frequency=220, duration=5000):
        super().__init__()
        self.frequency = frequency
        self.duration = duration
    
    def generate(self, sample_rate):
        return (2*np.pi* self.frequency * np.linspace(0, self.duration/1000, int(self.duration * sample_rate/1000), False) % (2*np.pi))-np.pi

class Step(Signal):
    def __init__(self, duration=1):
        super().__init__()
        self.duration = duration
    
    def generate(self, sample_rate):
        return np.ones((int(self.duration*sample_rate/1000),), dtype=np.float64)

class GreyNoise(Signal):
    def __init__(self, duration=5000):
        super().__init__()
        self.duration = duration
    
    def generate(self, sample_rate):
        return 2*np.random.rand(int(self.duration*sample_rate/1000)) - 1



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
    
    def generate(self, sample_rate):
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
    """
    TODO perhaps make Raw.cache instead
    (but make it easily extensible for new subclasses of Raw)
    either way, WAV/Raw objects should not contain
    the actual audio!
    just a key that will only be used in generate().
    this way the object is an empty skeleton.
    
    Raw.cache can be a dictionary with types as keys,
    values are actual caches with keys defined by each subclass individually
    """
    
    def __init__(self, filename):
        if filename in WAV.cache:
            audio = WAV.cache[filename].copy()
        else:
            audio = WAV_to_Audio(filename)
            WAV.cache[filename] = audio
        
        # TODO copy again? so the cache will be eternally independent?
        super().__init__(audio)
    






















