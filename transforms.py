# -*- coding: utf-8 -*-
"""
Created on Sun Aug 18 21:01:16 2019

@author: Dror
"""

import numpy as np
from audio import Audio

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
    def __init__(self, frequency, size):
        self.frequency = frequency
        self.size = size
    
    def realise(self, signal, audio):
        """ audio is Audio instance"""
        assert isinstance(audio, Audio) # TODO remove this after debug hopefully
        
        sin = np.sin(self.frequency * \
                     np.linspace(0, audio.duration(), audio.length(), False) * 2 * np.pi)
        audio *= (sin * self.size + (1-self.size))
        # remember [:] is necessary to retain changes
        

class Amplitude(Transform):
    """ simple increase/decrease of amplitude.
    don't use this directly; best to just use 0.34 * Signal for example. """
    def __init__(self, size):
        self.size = size
    
    def realise(self, signal, audio):
        audio = self.size*audio

class Shift(Transform):
    """ shifts the signal forward in time.
    it is problematic to use seconds all the time,
    because of floating point numbers TODO
    """
    def __init__(self, seconds):
        self.seconds = seconds
    
    def realise(self, signal, audio):
        audio.push_forward(int(self.seconds * signal.sample_rate/1000))

class Extend(Transform):
    """ adds silence after the signal. needed?
    """
    

class Channels(Transform):
    """ transforms mono to channels with the appropriate amps
    """
    def __init__(self, amps):
        """ amps is a tuple, [-1,1] for each of the required channels """
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
        self.pans = tuple([Pan.lambda_to_range(pan) for pan in pans])
    
    @staticmethod
    def lambda_to_range(f):
        """ transforms function from convenient lambda format to something usable
        for Pan.realise() """
        return lambda rng: np.asarray([f(x) for x in rng], dtype=np.float64)
    
    def realise(self, signal, audio):
        assert len(self.pans) in (1, audio.num_channels)
        
        if len(self.pans) < audio.num_channels:
            self.pans = (self.pans[0],) * audio.num_channels
            # TODO note that this is a side effect; though *shouldn't* harm anything
        
        for (i,pan) in enumerate(self.pans):
            amps = pan(range(audio.length()))
            audio.audio[i,:] *= amps
        
        
            










