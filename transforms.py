# -*- coding: utf-8 -*-
"""
Created on Sun Aug 18 21:01:16 2019

@author: Dror
"""

import numpy as np
from audio import Audio
from utils import lambda_to_range, DB_to_Linear, \
                  isnumber, iscallable, \
                  samples, samples_slice

class Transform:
    """ represents post-processing on some given signal.
    use __init__ to set the transform params,
    and realise for the implementation on the WAV.
    
    realise should directly change the audio of the signal element,
    and thus each transform can be bound to several signals without intereference.
    
    """
    
    def __init__(self):
        pass
    
    def __str__(self):
        return str(type(self).__name__)
    
    def samples(self, sample_rate):
        if not hasattr(self, "duration"):
            raise TypeError("transform.duration must be defined to support conversion to samples")
        return samples(self.duration, sample_rate)
    
    def realise(self, audio):
        """ here we apply the transformation on the Audio object.
        this should change the object directly, don't return anything."""
        pass

############################

class Fade(Transform):
    min_fade = -50
    
    def __init__(self, is_in=True, duration=3000):
        self.is_in = is_in
        self.duration = duration
    
    def realise(self, audio):
        amp = DB_to_Linear(np.linspace(Fade.min_fade, 0, self.samples(audio.sample_rate)))
        # perhaps the fade in should be nonlinear
        # TODO subsciprability problem
        
        if not self.is_in:
            amp[:] = amp[::-1]
        
        # TODO in case of fade out, if amp is shorter or longer than audio,
        # care must be taken when multiplying!
        audio *= amp
        # TODO TEST!!!!!!!!!!!!!
        # TODO I still hear a bump when the playback starts


class Gain(Transform):
    """
    Adds positive/negative gain in dBs to the signal.
    """
    def __init__(self, dB):
        self.dB = dB
    
    def realise(self, audio):
        audio.audio[:,:] *= DB_to_Linear(self.dB)

class Amplitude(Transform):
    """ simple increase/decrease of amplitude.
    for constant amplitude, don't use this directly;
    best to just use 0.34 * Signal syntax for example, which reverts to this class.
    use this for more complex amplitude functions
    
    use Gain() to change in dB
    """
    def __init__(self, size):
        self.size = size
        
        if iscallable(size):
            # TODO what if size is function, not lambda?
            self.size = lambda_to_range(size)
    
    def realise(self, audio):
        # TODO shouldn't this just affect a copy of audio????
        if isnumber(self.size):
            audio.audio = self.size*audio.audio
            return
        
        if iscallable(self.size):
            amps = self.size(audio.length(), audio.sample_rate)
            # TODO view or copy?
            # TODO what about different channels?
            audio.audio *= amps
        else:
            raise TypeError()


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
    
    def realise(self, audio):
        """ audio is Audio instance"""
        assert isinstance(audio, Audio) # TODO remove this after debug hopefully
        
        sin = np.sin(self.phase + self.frequency * \
                     np.linspace(0, audio.duration(), audio.length(), False) * 2 * np.pi)
        audio *= (sin * self.size + (1-self.size))
        # remember [:] is necessary to retain changes
        


class Limiter(Transform):
    """ Cuts any sample that exceed some amount.
    Amount can be an absolute value amplitude,
    or a ratio/percentage of the current maximum.
    
    minimum params are to limit from below in the range [-min,+min]
    which is just experimental
    """
    def __init__(self, max_amplitude=None, max_ratio=None, max_dB=None,
                       min_amplitude=None, min_ratio=None, min_dB=None):
        """ at most one max can to be non-None, at most one min as well"""
        assert (max_amplitude is not None) + (max_ratio is not None) + (max_dB is not None) <= 1
        assert (min_amplitude is not None) + (min_ratio is not None) + (min_dB is not None) <= 1
        
        #TODO more assertions
        
        if max_dB is not None or min_dB is not None:
            raise NotImplementedError
            # TODO
        
        self.is_min = not (min_amplitude is None and min_ratio is None and min_dB is None)        
        self.is_max = not (max_amplitude is None and max_ratio is None and max_dB is None)
        
        self.max_amplitude = max_amplitude
        self.max_ratio = max_ratio
        self.max_dB = max_dB
        self.min_amplitude = min_amplitude
        self.min_ratio = min_ratio
        self.min_dB = min_dB
    
    def realise(self, audio):
        # convert to the amplitude case then continue normally
        if self.is_max:
            if self.max_ratio is not None:
                self.max_amplitude = self.max_ratio*np.max(np.abs(audio.audio))
        
            # TODO do the same for dBs
            np.clip(audio.audio, -self.max_amplitude, self.max_amplitude, out=audio.audio)
        
        if self.is_min:
            if self.min_ratio is not None:
                self.min_amplitude = self.min_ratio*np.max(np.abs(audio.audio))
            #TODO same for dBs
            
            audio.audio[:,:] = np.sign(audio.audio) * \
                               np.clip(np.abs(audio.audio), a_min=self.min_amplitude, a_max=None)
        

#####################

class Shift(Transform):
    """ shifts the signal forward in time.
    it is problematic to use seconds all the time,
    because of floating point numbers TODO
    TODO
    """
    def __init__(self, duration):
        self.duration = duration
    
    def realise(self, audio):
        audio.push_forward(self.samples(audio.sample_rate))

class Extend(Transform):
    """ adds silence after the signal. needed?
    """
    def __init__(self, duration):
        self.duration = duration
    
    def realise(self, audio):
        audio.extend(self.samples(audio.sample_rate))

class Reverse(Transform):
    """
    reverses the signal
    """
    def __init__(self):
        pass
    
    def realise(self, audio):
        audio.audio[:,:] = audio.audio[:,::-1]

class Slice(Transform):
    """ returns only a specified part of the signal """
    def __init__(self, s):
        """ s is slice """
        # TODO filter slices (if relevant?)
        self.slice = s
    
    def realise(self, audio):
        audio.audio = audio.audio[:,samples_slice(self.slice, audio.sample_rate)]

class Combine(Transform):
    """ given another Signal as input, realises it and pushes it back
    into the affected signal in the relevant place.
    if the signal to push inside is too small, it will mean a silence gap,
    if too long, its remainder will be mixed into the continuation of the parent signal
    """
    def __init__(self, slice, signal):
        self.slice = slice
        self.signal = signal
    
    def realise(self, audio):
        # TODO support channels
        slc = samples_slice(self.slice, audio.sample_rate)
        
        new_audio = self.signal.realise(audio.sample_rate)
        
        audio.audio[:, slc] = 0
        audio.extend(slc.start+new_audio.length() - audio.length())
        audio.audio[:, slc.start:slc.start+new_audio.length()] += new_audio.audio

###### PANNING STUFF    

class Channels(Transform):
    """ transforms mono to channels with the appropriate amps
    """
    def __init__(self, amps):
        """ amps is a tuple, [-1,1] for each of the required channels """
        # TODO maybe better to use variable number of args instead of tuple, looks nicer
        self.amps = amps
    
    def realise(self, audio):
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
        # TODO better written with iscallable?
        # or isinstance(pans, (collections.Callable, tuple))?
        assert type(pans) in (type(lambda x:x), tuple), "invalid argument for Pan transform"
        
        if not isinstance(pans, tuple):
            pans = (pans,)
        
        # TODO find better conversion
        self.pans = tuple([lambda_to_range(pan) for pan in pans])
    
    def realise(self, audio):
        assert len(self.pans) in (1, audio.num_channels())
        
        if len(self.pans) < audio.num_channels():
            self.pans = (self.pans[0],) * audio.num_channels()
            # TODO note that this is a side effect; though *shouldn't* harm anything
        
        for (i,pan) in enumerate(self.pans):
            amps = pan(audio.length(), audio.sample_rate)
            audio.audio[i,:] *= amps
        

class Repan(Transform):
    """ Allows switching between channels.
    """
    def __init__(self, *channels):
        """ channels is a permutation on the existing channels.
        i.e. (1,0) switches left and right.
        None means leave channel empty.
        """
        assert isinstance(channels, tuple)
        self.channels = channels
    
    def realise(self, audio):
        new_audio = np.zeros(audio.audio.shape, dtype=np.float64)
        for i, channel in enumerate(self.channels):
            if channel is None:
                continue
            new_audio[i,:] = audio.audio[channel,:]
            
        audio.audio[:,:] = new_audio[:,:]


####### FILTERS #########

class Downsample_rough(Transform):
    """ skips samples. can hear the effects of aliasing.
    suppose factor is 3, then this copies all 3k-th samples into
    the 3k+1-th, 3k+2-th places.
    phase is supposed to let us choose 3k+1, 3k+2 as the main one for example
    # can be interesting to put 4k on L and 4k+2 on R, see if there is stereo effect
    """
    
    def __init__(self, factor=2, phase=0):
        self.factor = factor
        self.phase = phase
        assert isinstance(phase, int) and 0 <= phase < factor
        #assert phase == 0, "not implemented"
        if phase != 0:
            raise NotImplementedError # TODO
    
    def realise(self, audio):
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
        assert isinstance(weights, (int, tuple, list)), "weights argument should be either int or list/tuple"
        #assert isinstance(weights, int) or sum(weights) == 1, "weights must sum to 1"
        if isinstance(weights, int):
            weights = tuple(1 for w in range(weights))
        
        self.weights = weights
    
    def realise(self, audio):
        res = np.zeros((audio.audio.shape[0], audio.audio.shape[1] + len(self.weights) - 1), dtype=np.float64)
        
        for i, weight in enumerate(self.weights):
            res[:,i:audio.audio.shape[1]+i] += weight*audio.audio
        
        res /= sum(self.weights)
        
        pos = int(np.floor((len(self.weights) - 1)/2))
        # the index from which to start reading the averaged signal
        # (as it is longer due to time delays)
        
        audio.audio[:,:] = res[:, pos:pos+audio.audio.shape[1]]



###### EXPERIMENTS ######

class Convolution(Transform):
    """ is this the right name?
    squaring the signal, or multiplying by its own reverse
    """
    
    def __init__(self, forward=True, add=0, is_both_ways=False):
        self.forward = forward
        self.add = add
        self.is_both_ways = is_both_ways
    
    def realise(self, audio):
        # TODO the add works both ways to keep the signal away from zero
        # but we can also omit the sign thing, basically making the signal
        # more positive in general, and sounding less strange
        other = audio.audio[:,::(1 if self.forward else -1)]
        if self.is_both_ways:
            audio.audio[:,:] *= (self.add*np.sign(other) + other)
        else:
            audio.audio[:,:] *= (self.add + other)




















