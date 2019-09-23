# -*- coding: utf-8 -*-
"""
Created on Thu Aug 22 20:53:05 2019

@author: Dror
"""

import numpy as np
import copy
from utils import ints_by_width

class Audio:
    def __init__(self, num_channels, sample_rate):
        """ create empty.
        by convention duration is (mili?)seconds, length implies #samples.
        """
        #TODO do we really need to specify num channels?
        #would be cooler to implicitly figure it out from the signal
        assert(type(num_channels) == int and 1 <= num_channels)
        # TODO other assertions
        
        self.num_channels = num_channels
        self.sample_rate = sample_rate
        self.audio = np.zeros((num_channels,1), dtype=np.float64)
        # TODO is (..,1) good?
        return
    
    def is_mono(self):
        return self.num_channels == 1
    
    def length(self):
        return self.audio.shape[1]
    
    def duration(self):
        return self.length()/self.sample_rate
    
    def from_array(self, array):
        """
        converts np.ndarray to Audio.
        if array is not of type np.float64, converts it implicitly!
        """
        if len(array.shape) == 1:
            array.resize((1, array.shape[0]))
        
        self.__init__(array.shape[0], self.sample_rate)
        # TODO inefficient slightly for creating an empty array first
        self.audio = (array/np.max(array)).copy(order="C")
        return
    
    def copy(self):
        """
        creates an identical Audio object.
        """
        return copy.deepcopy(self)
    
    
    #######################
    
    # static functions for manipulating arrays
    
    @staticmethod
    def add_channels(array, channels):
        raise NotImplementedError
        pass
    
    @staticmethod
    def multiply_channels(array, channels):
        """
        assums (1,d) array. copies the first row d times
        """
        assert len(array.shape) == 2 and array.shape[0] == 1
        if channels == 0:
            return
        
        array.resize((channels, array.shape[1]), refcheck=False)
        array[:,:] = array[0,:]
        return
    
    ##################
    
    """
    
    first make sure other is appropriate type
    can be scalar (if multiply)
    or np.list, in which case we may need to add channels first
    
    length not restrictive
    
    """
    
    def conform(self, other):
        """
        ensures other is a 2-d ndarray of similar 1st shape,
        and that self.length >= other.length
        and that self has enough channels
        note that this function has side effects!
        """
        
        if isinstance(other, Audio):
            other = other.audio
        
        assert isinstance(other, np.ndarray)
        
        if len(other.shape) == 1:
            other.resize((1, other.shape[0]))
            # TODO this is used also in from_array
        
        assert other.shape[0] in (1, self.num_channels) or self.num_channels==1
        
        if other.shape[0] == 1:
            Audio.multiply_channels(other, self.num_channels)
        
        if self.num_channels == 1:
            self.from_mono(other.shape[0])
            # TODO do we need this method?
            # kinda repeats multiply_channelss
        
        self.extend(other.shape[1] - self.length())
        
        return other
        
    def __radd__(self, other):
        if other == 0:
            return self
        else:
            return other.__add__(self)
    
    def __add__(self, other):
        self.conform(other)
        self.audio[:,0:other.length()] += other.audio
        # TODO delete the other Audio??? for safety and memory
        return self
    
    
    def __rmul__(self, other):
        return self.__mul__(other)
    
    def __mul__(self, other):
        if type(other) == float: # TODO accept np.float too???
            # TODO shouldnt this affect the copy of self.audio only??
            self.audio *= other
            return self
        
        # TODO also does not support with Audios with differing params
        self.conform(other)
        self.audio[:,0:other.shape[1]] *= other[:,:]
        return self
    
    ###################
    
    
    ## prepare for mixdown
    
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
        TODO not all of these types are supported anyway
        """
        return audio.astype(ints_by_width[byte_width-1])
    
    def mixdown(self, byte_width, max_amplitude=1):
        assert max_amplitude == None or 0 < max_amplitude <= 1
        
        if max_amplitude == None:
            # don't touch the amplitudes unnecessarily
            max_amplitude = np.max(np.abs(self.audio))
        
        self.byte_width = byte_width
        
        audio = Audio.fit(self.audio, max_amplitude)
        audio = Audio.stretch(self.audio, self.byte_width)
        audio = Audio.integrate(audio, self.byte_width)
        
        self.buffer = np.zeros((self.length()*self.num_channels),
                               dtype=ints_by_width[self.byte_width-1],
                               order='C')
        
        for i in range(self.num_channels):
            self.buffer[i::self.num_channels] = audio[i]
        return self
    
    
    ###################
    
    def extend(self, how_much):
        """ extends all available channels with zeros """
        if how_much <= 0:
            return
        self.audio = np.pad(self.audio, ((0,0),(0,how_much)), mode="constant", constant_values=0.0)
        return
    
    def push_forward(self, how_much):
        """ pads the beginning with zeros """
        self.audio = np.pad(self.audio, ((0,0),(how_much,0)), mode="constant", constant_values=0.0)
        return
    
    
    
    def to_mono(self):
        """ combines all channels down to one. does not scale!
        """
        self.audio = np.sum(self.audio, 0)
        self.num_channels = 1
        return
    
    def from_mono(self, num_channels):
        """ duplicates a mono channel into various channels.
        does not scale! """
        assert self.num_channels == 1
        Audio.multiply_channels(self.audio, num_channels)
        self.num_channels = num_channels
        return
    
    def to_channel(self, num_channels, channel):
        """ adds new empty channels, putting the original signal in channel """
        assert 0 <= channel < num_channels
        # TODO assert num channels is valid
        self.audio.resize((num_channels, self.length()), refcheck=False)
        self.num_channels = num_channels
        
        if channel != 0:
            self.audio[channel,:] = self.audio[0, :]
            self.audio[0,:] = 0
        
        return
        
    
    