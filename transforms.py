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
    def __init__(self, is_in=True, duration=3):
        self.is_in = is_in
        self.duration = duration
    
    def realise(self, signal, audio):
        amp = np.linspace(0, 1, self.duration * signal.sample_rate)
        # perhaps the fade in should be nonlinear
        # TODO subsciprability problem
        shape = (0, self.duration * signal.sample_rate)
        
        np.pad(amp, (shape,), mode="constant", constant_values=1.0)
        
        if not self.is_in:
            amp[:] = amp[::-1]
            
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
        audio.push_forward(self.seconds * signal.sample_rate)

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
    












