# -*- coding: utf-8 -*-
"""
Created on Thu Aug 22 20:53:05 2019

@author: Dror

TODO
do we need all these functions as static?
some may be instance functions, some may belong in utils.
"""

import numpy as np
import copy
from utils import ints_by_width, is_number

class Audio:
    def __init__(self, sample_rate):
        self.sample_rate = sample_rate
        self.audio = np.zeros((1,1), dtype=np.float64)
        # TODO is (..,1) good?
    
    def num_channels(self):
        return self.audio.shape[0]
    
    def is_mono(self):
        return self.num_channels() == 1
    
    def length(self):
        return self.audio.shape[1]
    
    def duration(self):
        return self.length()/self.sample_rate
    
    
    #######################
        
    def __radd__(self, other):
        if other == 0:
            return self
        else:
            return other.__add__(self)
    
    def __add__(self, other):
        assert isinstance(other, Audio)
        self.conform(other)
        self.audio[:,0:other.length()] += other.audio
        # TODO delete the other Audio??? for safety and memory
        return self
    
    def __mul__(self, other):
        if isinstance(other, np.ndarray):
            assert len(other.shape) == 1, "can multiply Audio by np.ndarray only for one-dimensional arrays"
            if other.shape[0] > self.length():
                other = other[0:self.length]
            self.audio[:,0:other.shape[0]] *= other
            return
            
        assert isinstance(other, Audio)
        # for multiplying by a float, we multiply the signal instead
        # TODO also does not support with Audios with differing params
        self.conform(other)
        self.audio[:,0:other.length()] *= other[:,:]
        return self
    
    ###################
    
    def append(self, other):
        assert isinstance(other, Audio)
        self.conform(other, is_append=True)
        self.audio[:,-other.length():] += other.audio
        return self
    
    """
    
    first make sure other is appropriate type
    can be scalar (if multiply)
    or np.list, in which case we may need to add channels first
    
    length not restrictive
    
    """
    
    def conform(self, other, is_append=False):
        """
        reshapes self.audio so other.audio may be mixed into it.
        
        ensures other is a 2-d ndarray of similar 1st shape,
        and that self.length >= other.length
        and that self has enough channels
        note that this function has side effects for self.audio!
        
        and unfortunately also for other.
        """
        
        assert isinstance(other, Audio), "Audio.conform can only be used between Audios"
        assert other.is_mono() or self.is_mono or other.num_channels() == self.num_channels()
        
        if other.is_mono():
            other.from_mono(self.num_channels())
            # TODO warning: this affects other.
        
        if self.is_mono():
            self.from_mono(other.num_channels())
        
        self.extend(other.length() - self.length() if not is_append else other.length())
    
    def from_array(self, array):
        """
        converts np.ndarray to Audio.
        if array is not of type np.float64, converts it implicitly!
        note that this normalizes the values to be within [-1,1]
        """
        
        if len(array.shape) == 1:
            array.resize((1, array.shape[0]))
        
        # TODO inefficient slightly for creating an empty array first
        self.audio = np.zeros_like(array, dtype=np.float64)
        self.audio = (array/np.max(np.abs(array))).copy(order="C")
    
    def copy(self):
        """
        creates an identical Audio object.
        """
        return copy.deepcopy(self)
    
    
    def extend(self, how_much):
        """ extends all available channels with zeros """
        if how_much <= 0: # this can happen
            return
        self.audio = np.pad(self.audio, ((0,0),(0,how_much)), mode="constant", constant_values=0.0)
    
    def push_forward(self, how_much):
        """ pads the beginning with zeros """
        self.audio = np.pad(self.audio, ((0,0),(how_much,0)), mode="constant", constant_values=0.0)
    
    
    
    def to_mono(self):
        """ combines all channels down to one. does not scale!
        """
        self.audio = np.sum(self.audio, 0)
    
    def from_mono(self, num_channels):
        """ duplicates a mono channel into various channels.
        does not scale! """
        assert self.is_mono(), "Can't call Audio.from_mono() for non-mono Audio."
        if num_channels == 1:
            return
        self.audio.resize((num_channels, self.length()), refcheck=False)
        self.audio[:,:] = self.audio[0,:]
    
    def to_channel(self, num_channels, channel):
        """ adds new empty channels, putting the original signal in channel """
        assert 0 <= channel < num_channels
        # TODO assert num channels is valid
        self.audio.resize((num_channels, self.length()), refcheck=False)
        
        if channel != 0:
            self.audio[channel,:] = self.audio[0, :]
            self.audio[0,:] = 0
        
    ##################
    
    # static functions for manipulating arrays
    
    @staticmethod
    def add_channels(array, channels):
        raise NotImplementedError
        pass
    
    ###################
    
    ## prepare for mixdown
    """
    we have these as static since in Audio.mixdown(), we do not wish
    to affect self.audio.
    """
    
    @staticmethod
    def fit(audio, max_amplitude):
        """
        stretches/squashes the amplitude of the samples to be [-max_amplitude, +max_amplitude]
        given that max_amplitude <= 1.
        
        to disable fitting unless necessary, set max_amplitude = np.max(np.abs(audio))
        TODO perhaps do this differently (set max_amplitude=None?)
        """
        if max_amplitude > 1:
            max_amplitude = 1
            print("Squashing amplitudes...")
        
        return audio * max_amplitude / np.max(np.abs(audio))
        
    # TODO move these to utils?
    @staticmethod
    def stretch(audio, byte_width):
        """ stretches the samples to cover a range of width 2**bits,
        so we can convert to ints later.
        """
        return audio * (2**(8*byte_width-1) - 1)
    
    @staticmethod
    def integrate(audio, byte_width):
        """
        conversion from floats to integers
        """
        if byte_width not in (1,2):
            print("byte width may not be supported. try 1 or 2.")
        return audio.astype(ints_by_width[byte_width-1])
    
    def mixdown(self, byte_width, max_amplitude=1):
        """
        side effects are only the creation of self.byte_width and self.buffer.
        self.audio remains unaffected, and we use static methods for this end.
        """
        assert max_amplitude == None or 0 < max_amplitude <= 1
        
        if max_amplitude == None:
            # don't touch the amplitudes unnecessarily
            max_amplitude = np.max(np.abs(self.audio))
        
        self.byte_width = byte_width
        
        audio = Audio.fit(self.audio, max_amplitude)
        audio = Audio.stretch(audio, self.byte_width)
        audio = Audio.integrate(audio, self.byte_width)
        
        self.buffer = np.zeros((self.length()*self.num_channels()),
                                dtype=ints_by_width[self.byte_width-1],
                                order='C')
        # TODO note that byte_width, buffer etc. are modified by this function
        # for this class it may be fine, because this is where
        # all the processing acctually happens on
        # operation table
        for i in range(self.num_channels()):
            self.buffer[i::self.num_channels()] = audio[i]
        return self












    
    