# -*- coding: utf-8 -*-

import numpy as np

from gensound.utils import isnumber
from gensound.curve import Curve
from gensound.transforms import Transform, Convolution

class OneImpulseReverb(Convolution):
    def __init__(self, mix=0.5, num=1000, curve="linear"):
        if curve == "linear":
            self.response = np.linspace(mix, 0, num=num)
        elif curve == "steep":
            self.response = 1/np.linspace(1, num, num=num)
        
        self.response.resize((1, self.response.shape[0]))
        # TODO call super().__init__ instead?
        

class Vibrato(Transform):
    """ Vibrato
    This Transform performs a vibrato effect on the audio, shifting the pitch up and down
    according to a Sine pattern.
    
    frequency - this is the 'speed' of the vibrato in Hz
    width - this is the vibrato width (maximal pitch shift), measured in semitones.
    """
    def __init__(self, frequency, width):
        # width in semitones (will go that same amount both up and down, total width is twice that)
        self.frequency = frequency # can receive Curve
        self.width = width
    
    def realise(self, audio):
        if not isinstance(self.frequency, Curve):
            width_samples = (2**(self.width/12) - 1)/(2*np.pi*self.frequency)*audio.sample_rate
            
            indices = np.arange(0, audio.length, 1, dtype=np.float64)
            indices += width_samples*np.sin(2*np.pi/audio.sample_rate*self.frequency * indices)
            indices[indices > audio.length-1] = audio.length - 1
            audio.audio[:,:] = audio[:, indices[:]]
        else: # suppose width constant
            width_samples = (2**(self.width/12) - 1)/(2*np.pi*self.frequency.flatten(audio.sample_rate))*audio.sample_rate
            
            indices = np.arange(0, audio.length, 1, dtype=np.float64)
            indices += width_samples * np.sin(2*np.pi * self.frequency.integral(audio.sample_rate)[:-1])
            indices[indices > audio.length-1] = audio.length - 1
            audio.audio[:,:] = audio[:, indices[:]]
            




class Stretch(Transform):
    """ Stretches audio by a certain factor, or to a desired duration,
    using interpolation.
    """
    # TODO parametric stretch!
    def __init__(self, rate=None, duration=None, method="quadratic"):
        """ exactly one of factor, duration should be defined.
        factor = ratio of speed up/slow down. (1=no difference, 2=twice as fast)
        duration = stretch/shrink to this duration (milliseconds or samples)
        """
        self.rate = rate
        self.duration = duration
        self.method = method
    
    def realise(self, audio):
        assert (self.rate is None) + (self.duration is None) == 1, "Stretch: exactly one of the arguments rate, duration, must be defined."
        from gensound.utils import get_interpolation
        interpolate = get_interpolation(self.method)
        
        if self.rate is None: # compute from duration
            factor = audio.length / self.num_samples(audio.sample_rate)
            audio.audio = interpolate(audio.audio, np.arange(0, audio.length-1, factor))
        elif isnumber(self.rate):
            factor = self.rate
            audio.audio = interpolate(audio.audio, np.arange(0, audio.length-1, factor))
        elif isinstance(self.rate, Curve):
            indices = self.rate.integral(audio.sample_rate)*audio.sample_rate
            
            if max(indices) < audio.length-1: # if curve is shorter, keep using the final value till the audio runs out
                indices = np.concatenate((indices, np.arange(max(indices), audio.length-1, self.rate.endpoint())))
            else:
                indices = indices[indices < audio.length-1] # if curve lasts longer than the resulting stretched audio
                
            audio.audio = interpolate(audio.audio, indices)
        else:
            raise Exception("Invalid arguments for Stretch.")
        
        


class Downsample(Transform):
    """ skips samples. can hear the effects of aliasing.
    suppose factor is 3, then this copies all 3k-th samples into
    the 3k+1-th, 3k+2-th places.
    phase is supposed to let us choose 3k+1, 3k+2 as the main one for example
    # can be interesting to put 4k on L and 4k+2 on R, see if there is stereo effect
    """
    
    def __init__(self, factor, phase=0):
        assert isinstance(factor, int), "factor argument of Downsample should be an integer."
        assert isinstance(phase, int) and 0 <= phase < factor
        #assert phase == 0, "not implemented"
        if phase != 0:
            raise NotImplementedError # TODO
            
        self.factor = factor
        self.phase = phase
        
    
    def realise(self, audio):
        l = audio.length #- self.phase
        
        for i in range(1, self.factor):
            less = 0 != (l % self.factor) <= i
            audio.audio[:,i::self.factor] = audio.audio[:,0:l + (-self.factor if less else 0):self.factor]
            #audio.audio[:,i::self.factor] = audio.audio[:,self.phase:l + (-self.factor if less else 0):self.factor]








