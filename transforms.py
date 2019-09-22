# -*- coding: utf-8 -*-
"""
Created on Sun Aug 18 21:01:16 2019

@author: Dror
"""

import numpy as np
from audio import Audio

def lambda_to_range(f):
    """ transforms function from convenient lambda format to something usable
    for Pan and Amplitude (i.e. shift-sensitive transforms)
    """
    return lambda length, sample_rate: np.asarray([f(x/sample_rate) for x in range(length)], dtype=np.float64)
    # TODO this does not take sample rate into account!

class Transform:
    """ represents post-processing on some given signal.
    use __init__ to set the transform params,
    and realise for the implementation on the WAV.
    
    realise should directly change the audio of the signal element,
    and thus each transform can be bound to several signals without intereference.
    
    """
    
    def __init__(self):
        pass
    
    def realise(self, signal, audio):
        """ here we apply the transformation on the Audio object.
        this should change the object directly, don't return anything."""
        pass


class Fade(Transform):
    def __init__(self, is_in=True, duration=3000):
        self.is_in = is_in
        self.duration = duration
    
    def realise(self, signal, audio):
        amp = np.linspace(0, 1, int(self.duration * signal.sample_rate/1000))
        # perhaps the fade in should be nonlinear
        # TODO subsciprability problem
        
        if not self.is_in:
            amp[:] = amp[::-1]
        
        # TODO in case of fade out, if amp is shorter or longer than audio,
        # care must be taken when multiplying!
        audio *= amp
        return # TODO TEST!!!!!!!!!!!!!

class AmpFreq(Transform):
    """
    have the amplitude change according to a sine function over time continuously,
    with given width (size) and frequency
    TODO again the factors should be perhaps logarithimic
    """
    def __init__(self, frequency, size, phase=0):
        self.frequency = frequency
        self.size = size
        self.phase = phase
    
    def realise(self, signal, audio):
        """ audio is Audio instance"""
        assert isinstance(audio, Audio) # TODO remove this after debug hopefully
        
        sin = np.sin(self.phase + self.frequency * \
                     np.linspace(0, audio.duration(), audio.length(), False) * 2 * np.pi)
        audio *= (sin * self.size + (1-self.size))
        # remember [:] is necessary to retain changes
        

class Amplitude(Transform):
    """ simple increase/decrease of amplitude.
    for constant amplitude, don't use this directly;
    best to just use 0.34 * Signal syntax for example, which reverts to this class.
    use this for more complex amplitude functions
    """
    def __init__(self, size):
        self.size = size
        
        if type(size) == type(lambda x:x):
            # TODO what if size is function, not lambda?
            self.size = lambda_to_range(size)
    
    def realise(self, signal, audio):
        # TODO shouldn't this just affect a copy of audio????
        if type(self.size) == float:
            audio = self.size*audio
            return
        
        if type(self.size) == type(lambda x:x):
            amps = self.size(audio.length(), audio.sample_rate)
            # TODO view or copy?
            # TODO what about different channels?
            audio.audio *= amps

class Shift(Transform):
    """ shifts the signal forward in time.
    it is problematic to use seconds all the time,
    because of floating point numbers TODO
    TODO
    """
    def __init__(self, duration):
        self.duration = duration
    
    def realise(self, signal, audio):
        audio.push_forward(int(self.duration * signal.sample_rate/1000))

class Extend(Transform):
    """ adds silence after the signal. needed?
    """
    def __init__(self, duration=1000):
        self.duration = duration
    
    def realise(self, signal, audio):
        # TODO can we avoid passing signal in, for all transforms?
        audio.extend(int(self.duration*signal.sample_rate/1000))


###### PANNING STUFF    

class Channels(Transform):
    """ transforms mono to channels with the appropriate amps
    """
    def __init__(self, amps):
        """ amps is a tuple, [-1,1] for each of the required channels """
        # TODO maybe better to use variable number of args instead of tuple, looks nicer
        self.amps = amps
    
    def realise(self, signal, audio):
        audio.from_mono(len(self.amps))
        for (i,amp) in enumerate(self.amps):
            audio.audio[i,:] *= amp
    
class Pan(Transform):
    """ applies arbitrary function to amplitudes of all channels
    """
    def __init__(self, pans):
        """ pans is either a function (range) -> ndarray(float64), or a tuple of these
        wrong, right now accepting functions R -> R
        """
        assert type(pans) in (type(lambda x:x), tuple), "invalid argument for Pan transform"
        
        if type(pans) != tuple:
            pans = (pans,)
        
        # TODO find better conversion
        self.pans = tuple([lambda_to_range(pan) for pan in pans])
    
    def realise(self, signal, audio):
        assert len(self.pans) in (1, audio.num_channels)
        
        if len(self.pans) < audio.num_channels:
            self.pans = (self.pans[0],) * audio.num_channels
            # TODO note that this is a side effect; though *shouldn't* harm anything
        
        for (i,pan) in enumerate(self.pans):
            amps = pan(audio.length(), audio.sample_rate)
            audio.audio[i,:] *= amps
        

class Repan(Transform):
    """ Allows switching between channels
    """
    def __init__(self, channels):
        """ channels is a permutation on the existing channels.
        i.e. (1,0) switches left and right.
        """
        assert type(channels) == tuple
        self.channels = channels
    
    def realise(self, signal, audio):
        raise NotImplementedError
        pass

#######

class Downsample_rough(Transform):
    """ skips samples. can hear the effects of aliasing.
    suppose factor is 3, then this copies all 3k-th samples into
    the 3k+1-th, 3k+2-th places.
    phase is supposed to let us choose 3k+1, 3k+2 as the main one for example
    """
    
    def __init__(self, factor=2, phase=0):
        self.factor = factor
        self.phase = phase
        assert type(phase) == int and 0 <= phase < factor
        #assert phase == 0, "not implemented"
        if phase != 0:
            raise NotImplementedError # TODO
    
    def realise(self, signal, audio):
        l = audio.audio.shape[1] #- self.phase
        
        for i in range(1, self.factor):
            less = 0 != (l % self.factor) <= i
            audio.audio[:,i::self.factor] = audio.audio[:,0:l + (-self.factor if less else 0):self.factor]
            #audio.audio[:,i::self.factor] = audio.audio[:,self.phase:l + (-self.factor if less else 0):self.factor]


class Average_samples(Transform):
    """ averages each sample with its neighbors, possible to specify weights as well.
    effectively functions as a low pass filter, without the aliasing effects
    of downsample rough.
    """
    
    def __init__(self, weights):
        """
        weights is int -> average #weights neighboring samples
        weights is tuple -> average len(weights) neighboring samples,
                            according to specified weights. will be normalized to 1.
        TODO: on the edges this causes a small fade in fade out of length len(weights).
        not necessarily a bug though.
        """
        assert type(weights) in (int, tuple, list), "weights argument should be either int or list/tuple"
        #assert type(weights) == int or sum(weights) == 1, "weights must sum to 1"
        if type(weights) == int:
            weights = tuple(1 for w in range(weights))
        
        self.weights = weights
    
    def realise(self, signal, audio):
        res = np.zeros((audio.audio.shape[0], audio.audio.shape[1] + len(self.weights) - 1), dtype=np.float64)
        
        for i, weight in enumerate(self.weights):
            res[:,i:audio.audio.shape[1]+i] += weight*audio.audio
        
        res /= sum(self.weights)
        
        pos = int(np.floor((len(self.weights) - 1)/2))
        # the index from which to start reading the averaged signal
        # (as it is longer due to time delays)
        
        audio.audio[:,:] = res[:, pos:pos+audio.audio.shape[1]]


class Reverse(Transform):
    """
    reverses the signal
    """
    def __init__(self):
        pass
    
    def realise(self, signal, audio):
        audio.audio[:,:] = audio.audio[:,::-1]


