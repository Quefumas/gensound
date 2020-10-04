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
from gensound.utils import ints_by_width

class Audio:
    """Basically a wrapper for a numpy array, representing the signal.
    Shape is (tracks, samples), tracks being >= 1.
    This object is mostly dealt with inside Transform and Signal functions,
    and typically should not be used directly unless you're creating new
    Signals or Transforms.
    Don't override too many operators - this is the nuts and bolts,
    not the pretty facade.
    """
    def __init__(self, sample_rate):
        self.shift = 0
        self.sample_rate = sample_rate
        # TODO get rid of sample_rate argument and have optional audio argument
        # that can be np.ndarray or other array or something
        self.audio = np.zeros((1, 0), dtype=np.float64)
    
    def ensure_2d(self):
        """ makes sure self.audio is 2-dimensional,
        since this is not obvious for mono signals.
        """
        # TODO make sure this is called in a hermetic fashion, everywhere it is needed
        if len(self.audio.shape) == 1:
            self.audio.resize((1, self.audio.shape[0]))
            return False # indicating it wasn't 2d
        return True # the shape was fine all along
        
    
    def from_array(self, array):
        """
        converts np.ndarray to Audio.
        if array is not of type np.float64, converts it implicitly!
        note that this normalizes the values to be within [-1,1]
        """
        if not isinstance(array, np.ndarray):
            array = np.asarray(array, dtype=np.float64)
        
        self.audio = array
        self.ensure_2d()
        
        # TODO should we copy?
        # note that this is called practically everytime we generate() a signal!!!
        self.audio = self.audio.copy(order="C")
        
        return self
    
    def copy(self):
        """
        creates an identical Audio object.
        """
        return copy.deepcopy(self)
    
    ####### getters #######
    
    # always get the info from self.audio itself;
    # we manipulate it directly all the time
    @property
    def num_channels(self):
        assert len(self.audio.shape) == 2
        return self.audio.shape[0]
    
    @property
    def is_mono(self):
        return self.num_channels == 1
    
    @property
    def length(self):
        assert len(self.audio.shape) == 2
        return self.audio.shape[1]
    
    def duration(self):
        # TODO this appears to be the only method the uses self.sample_rate
        # consider having it as an argument instead of instance variable
        return self.length/self.sample_rate
    
    @property
    def shape(self): # TODO consider doing others like this
        return self.audio.shape
    
    abs_start = lambda self: self.shift # in samples only
    abs_end = lambda self: self.shift+self.length
    
    ######### Unary manipulations #########
    
    """
    
    first make sure other is appropriate type
    can be scalar (if multiply)
    or np.list, in which case we may need to add channels first
    
    length not restrictive
    
    """
    
    def conform(self, other):
        """
        reshapes self.audio so other.audio may be mixed into it.
        
        ensures other is a 2-d ndarray of similar 1st shape,
        and that self.length >= other.length
        and that self has enough channels
        note that this function has side effects for self.audio!
        
        and unfortunately also for other.
        """
        
        assert isinstance(other, Audio), "Audio.conform can only be used between Audios"
        assert other.is_mono or self.is_mono or other.num_channels == self.num_channels
        
        # conforming channels
        if other.is_mono:
            other.from_mono(self.num_channels)
            # TODO warning: this affects other.
        
        if self.is_mono:
            self.from_mono(other.num_channels)
        
        # conforming lengths TODO better way?
        start = min(self.abs_start(), other.abs_start())
        end = max(self.abs_end(), other.abs_end())
        self.push_forward(self.abs_start() - start)
        self.to_length(end - start)
        
    
    
    ### time manipulations ###
    
    def to_length(self, length):
        """ Ensures self.length is at least length, padding with zeros if needed.
        """
        # TODO this and extend, do we need both?
        if self.length >= length:
            return
        
        self.extend(length - self.length)
    
    def extend(self, how_much):
        """ extends all available channels with zeros """
        self.audio = np.pad(self.audio, ((0,0),(0,how_much)), mode="constant", constant_values=0.0)
    
    def push_forward(self, how_much):
        """ pads the beginning with zeros """
         # TODO sister function which truncates beginning when shift < 0? for use in Combine
        if how_much < 0:
            return
        # pad with nothing before and after the channel dimension
        # pad with how_much before the time dimension, 0 after
        self.audio = np.pad(self.audio, ((0,0),(how_much,0)), mode="constant", constant_values=0.0)
        self.shift -= how_much
    
    
    ### channel manipulations ###
    
    def to_mono(self):
        """ mixes all channels down to one. does not scale!
        """
        self.audio = np.sum(self.audio, 0)
    
    def from_mono(self, num_channels):
        """ duplicates a mono channel into various channels.
        does not scale! """
        assert self.is_mono, "Can't call Audio.from_mono() for non-mono Audio."
        if num_channels == 1:
            return
        self.audio = self.audio.copy() # TODO is this wasteful?
        self.audio.resize((num_channels, self.length), refcheck=False)
        self.audio[:,:] = self.audio[0,:]
        assert self.ensure_2d()
    
    def to_channels(self, num_channels):
        """ ensures there are at least num_channels
        """
        shape = (num_channels-self.num_channels, self.length)
        self.audio = np.vstack((self.audio, np.zeros(shape, dtype=np.float64)))
    
    ######## binary operations ###########
    
    def mix(self, other):
        assert isinstance(other, Audio)
        
        self.conform(other)
        self.audio[:,other.abs_start()-self.abs_start():other.abs_start()-self.abs_start()+other.length] += other.audio
        return self
    
    def concat(self, other):
        assert isinstance(other, Audio)
        
        other.shift += self.length
        self.mix(other)
    
    
    
    ######## Overloading Operators ###########
    ## TODO consider overloading __setitem__, __getitem__,
    # so that we can do operations on audio instead of audio.audio
    # (or is it being too wordy here?)
    # also, choosing a single channel (not a slice) can be dealt with in the process,
    # delegating this responsibility away from Signal.__subscripts
    
    def __radd__(self, other):
        if other == 0:
            return self
        else:
            return other.__add__(self)
    
    def __add__(self, other): # do we want to overload this?
        return self.mix(other)
    
    def __mul__(self, other):
        print("convolution, should not happen")
        # TODO this should be reexamined and perhaps moved into Convolution or sth
        # also delegate to a non-overloaded function first
        if isinstance(other, np.ndarray):
            assert len(other.shape) == 1, "can multiply Audio by np.ndarray only for one-dimensional arrays"
            if other.shape[0] > self.length:
                other = other[0:self.length]
            self.audio[:,0:other.shape[0]] *= other
            return
            
        assert isinstance(other, Audio)
        # for multiplying by a float, we multiply the signal instead
        # TODO also does not support with Audios with differing params
        self.conform(other)
        self.audio[:,other.abs_start()-self.abs_start():other.abs_start()-self.abs_start()+other.length] *= other[:,:]
        return self
    
    
    
    
    
    
    
    ######## prepare for mixdown ########
    """
    we have these as static since in Audio.mixdown(), we do not wish
    to affect self.audio.
    """
    
    @staticmethod
    def fit(audio, max_amplitude=1):
        """
        stretches/squashes the amplitude of the samples to be [-max_amplitude, +max_amplitude]
        for max_amplitude <= 1.
        
        for max_amplitude = None, leave things as they are.
        """
        assert max_amplitude is None or 0 < max_amplitude
        
        if max_amplitude == None:
            return audio
        
        max_amp = np.max(np.abs(audio))
        return audio * (max_amplitude / max_amp) if max_amp != 0 else audio
        
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
        
        self.byte_width = byte_width
        
        audio = Audio.fit(self.audio, max_amplitude)
        audio = Audio.stretch(audio, self.byte_width)
        audio = Audio.integrate(audio, self.byte_width)
        
        self.buffer = np.zeros((self.length*self.num_channels),
                                dtype=ints_by_width[self.byte_width-1],
                                order='C')
        # TODO note that byte_width, buffer etc. are modified by this function
        # for this class it may be fine, because this is where
        # all the processing acctually happens on
        # operation table
        for i in range(self.num_channels):
            self.buffer[i::self.num_channels] = audio[i]
        return self












    
    