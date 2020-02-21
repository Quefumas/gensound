# -*- coding: utf-8 -*-
"""
Created on Sat Aug 17 21:41:28 2019

@author: Dror
"""

import copy

import numpy as np

from transforms import Transform, Amplitude, Slice, Combine
from audio import Audio
from playback import WAV_to_Audio
from utils import isnumber, samples

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
        new: can also return Audio if there is a need;
        but generally should be np.ndarray
        """
        pass
    
    def realise(self, sample_rate):
        """ returns Audio instance.
        parses the entire signal tree recursively
        """
        
        signal = self.generate(sample_rate)
        
        if not isinstance(signal, Audio):
            audio = Audio(sample_rate)
            audio.from_array(signal)
        else:
            audio = signal
    
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
        audio = self.realise(sample_rate)
        return audio.mixdown(byte_width, max_amplitude)
    
    #####################
    def samples(self, sample_rate):
        return samples(self.duration, sample_rate)
        
    def copy(self):
        """
        creates an identical signal object.
        """
        return copy.deepcopy(self)
    
    @staticmethod
    def concat(*args):
        return Sequence(*args)
    
    @staticmethod
    def mix(*args):
        # we really want to use #reduce(, args) instead
        # but the question is what should be the 1st argument?
        return sum(args)
    
    ####### sound operations ########
    
    def _amplitude(self, number):
        assert isnumber(number)
        return self*Amplitude(size=number)
    
    def _apply(self, transform):
        if not isinstance(transform, Transform):
            return self._amplitude(transform)
        
        s = self.copy() # TODO is this needed?
        # it is, so we can reuse the same base signal multiple times
        s.transforms.append(transform)
        return s
    
    def _concat(self, other):
        # TODO consider enabling for negative other,
        # thus shifting a sequence forward(backward? Chinese) in time
        # TODO possibly better way to implement than using Silence
        if isnumber(other):
            other = Silence(duration=other)
            
        s = Sequence()
        
        if not self.transforms and isinstance(self, Sequence):
            s.sequence += self.sequence
        else:
            s.sequence += [self]
        
        if not other.transforms and isinstance(other, Sequence):
            s.sequence += other.sequence
        else:
            s.sequence += [other]
        
        return s
    
    def _mix(self, other):
        s = Mix()
        
        if not self.transforms and isinstance(self, Mix):
            s.signals += self.signals
        else:
            s.signals += [self]
        
        if not other.transforms and isinstance(other, Mix):
            s.signals += other.signals
        else:
            s.signals += [other]
        
        return s
    
    def _repeat(self, number):
        # repeats this signal several times in a row
        assert isinstance(number, int)
        return Signal.concat(*[self]*number)
    
    def _print_nice(self):
        if isinstance(self, Sequence):
            res = "[{}]".format(" + ".join([str(signal) for signal in self.sequence]))
        elif isinstance(self, Mix):
            res = "({})".format(" + ".join([str(signal) for signal in self.signals]))
        else:
            res = str(type(self).__name__)
        
        res += "" if not self.transforms else "*({})".format(",".join([str(transform) for transform in self.transforms]))
        return res
    
    ####### overloading operators #######
    
    def __str__(self):
        return self._print_nice()
    
    def __pow__(self, other):
        return self._repeat(other)
    
    def __rmul__(self, other):
        """ multiplication from the left is only legal for numbers, not for transforms"""
        return self._amplitude(other)
    
    def __mul__(self, other):
        """
        signals can be multiplied on the right by both floats and transforms
        """
        return self._apply(other)
    
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
        return self._mix(other)
    
    def __sub__(self, other):
        return self._mix(-other)
    
    def __neg__(self):
        return self._amplitude(-1.0)
    
    def __or__(self, other):
        """Overloading concat."""
        return self._concat(other)
    
    def __ror__(self, other):
        if other == 0:
            return self
        
        if isnumber(other):
            return Silence(duration=other)._concat(self)
        
        raise TypeError("Signal can only be concatted to other signals, or to 0.")
    
    #########
    def __getitem__(self, *args):
        # no channels yet TODO
        assert isinstance(args[0], slice)
        return self.copy()*Slice(args[0])
    
    def __setitem__(self, *args):
        # no channels yet TODO
        assert isinstance(args[0], slice)
        assert isinstance(args[1], Signal) # TODO what are my requirements for the other stuff? to be signal?
        
        self.transforms.append(Combine(args[0], args[1]))
    
#### other "high-level" signals

class Mix(Signal):
    """
    a list of signals to be mixed together
    (AKA "internal node" of the mix tree)
    """
    def __init__(self, *signals):
        super().__init__()
        self.signals = list(signals)
    
    def generate(self, sample_rate):
        audio = Audio(sample_rate)
        
        for signal in self.signals:
            audio += signal.realise(sample_rate)
        
        return audio

class Sequence(Signal):
    """
    a list of signals to be placed one after the other
    """
    def __init__(self, *sequence):
        super().__init__()
        self.sequence = list(sequence)
    
    def generate(self, sample_rate):
        audio = Audio(sample_rate)
        
        for signal in self.sequence:
            audio.append(signal.realise(sample_rate))
        
        return audio

#### particular signals

class Silence(Signal):
    def __init__(self, duration=5000):
        super().__init__()
        self.duration = duration
    
    def generate(self, sample_rate):
        return np.zeros(self.samples(sample_rate), dtype=np.float64)

class Sine(Signal):
    def __init__(self, frequency=220, duration=5000):
        super().__init__()
        self.frequency = frequency
        self.duration = duration
        
    def generate(self, sample_rate):
        return np.sin(self.frequency * np.linspace(0, self.duration/1000, self.samples(sample_rate), False) * 2 * np.pi)
    
class Triangle(Signal):
    def __init__(self, frequency=220, duration=5000):
        super().__init__()
        self.frequency = frequency
        self.duration = duration
    
    def generate(self, sample_rate):
        # strange manipulation on sawtooth
        return 2*np.abs((2*np.pi* self.frequency * np.linspace(0, self.duration/1000, self.samples(sample_rate), False) % (2*np.pi))-np.pi)-np.pi
    
    
class Square(Signal):
    def __init__(self, frequency=220, duration=5000):
        super().__init__()
        self.frequency = frequency
        self.duration = duration
    
    def generate(self, sample_rate):
        return (((2*np.pi* self.frequency * np.linspace(0, self.duration/1000, self.samples(sample_rate), False) % (2*np.pi)) < np.pi) - np.pi).astype(np.float64)

class Sawtooth(Signal):
    def __init__(self, frequency=220, duration=5000):
        super().__init__()
        self.frequency = frequency
        self.duration = duration
    
    def generate(self, sample_rate):
        return (2*np.pi* self.frequency * np.linspace(0, self.duration/1000, self.samples(sample_rate), False) % (2*np.pi))-np.pi

class Step(Signal):
    def __init__(self, duration=1):
        super().__init__()
        self.duration = duration
    
    def generate(self, sample_rate):
        return np.ones((self.samples(sample_rate),), dtype=np.float64)

class GreyNoise(Signal):
    def __init__(self, duration=5000):
        super().__init__()
        self.duration = duration
    
    def generate(self, sample_rate):
        return 2*np.random.rand(self.samples(sample_rate)) - 1



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
    






















