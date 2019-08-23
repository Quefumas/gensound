# -*- coding: utf-8 -*-
"""
Created on Thu Aug 22 20:53:05 2019

@author: Dror
"""

import numpy as np

class Audio:
    def __init__(self, length, num_channels, sample_rate):
        """ create empty.
        by convention duration is (mili?)seconds, length implies #samples.
        """
        assert(type(num_channels) == int and 1 <= num_channels)
        # TODO other assertions
        
        self.num_channels = num_channels
        self.sample_rate = sample_rate
        self.length = length
        self.audio = np.zeros((num_channels,length), dtype=np.float64)
        return
    
    def is_mono(self):
        return self.num_channels == 1
    
    
    def from_array(self, array, sample_rate):
        """
        converts np.ndarray to Audio.
        """
        if len(array.shape) == 1:
            array.resize((1, array.shape[0]))
        
        self.__init__(array.shape[1], array.shape[0], sample_rate)
        # TODO inefficient slightly for creating an empty array first
        self.audio = array
        return
    
    
    
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
            return other.audio
        
        assert isinstance(other, np.ndarray)
        
        if len(other.shape) == 1:
            other.resize((1, other.shape[0]))
            # TODO this is used also in from_array
        
        assert other.shape[0] in (1, self.num_channels)
        
        if other.shape[0] == 1:
            Audio.multiply_channels(other, self.num_channels)
        
        if self.num_channels == 1:
            self.from_mono(other.shape[0])
            # TODO do we need this method?
            # kinda repeats multiply_channelss
        
        self.extend(other.shape[1] - self.length)
        
        return other
        
    
    def __add__(self, other):
        self.audio[:,0:other.length] += self.conform(other)
        # TODO delete the other Audio??? for safety and memory
        return self
    
    
    def __mul__(self, other):
        if type(other) == float: # TODO accept np.float too???
            self.audio *= other
            return self
        
        # TODO also does not support with Audios with differing params
        self.conform(other)
        self.audio[:,0:other.shape[1]] *= other[:,:]
        return self
    
    ###################
    
    
    ## prepare for mixdown
    
    def stretch(self):
        """ stretches/squashes the samples to be in the range [-1,1],
        to increase the dynamic range.
        in the future this step is to be further examined
        """
        self.audio = self.audio * (2**(8*self.byte_width-1) - 1) / np.max(np.abs(self.audio))
        return
    
    def integrate(self):
        self.audio = self.audio.astype((np.int8, np.int16, np.int32, np.int64)[self.byte_width-1])
        # TODO use new variable? or just return without saving?
        # to avoid self.audio being potentially of two different types
        return
    
    def mixdown(self, byte_width):
        self.byte_width = byte_width
        self.stretch()
        self.integrate()
        return self.audio
    
    
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
        self.audio.resize((num_channels, self.length), refcheck=False)
        self.num_channels = num_channels
        
        if channel != 0:
            self.audio[channel,:] = self.audio[0, :]
            self.audio[0,:] = 0
        
        return
        
    
    