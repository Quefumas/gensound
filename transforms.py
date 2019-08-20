# -*- coding: utf-8 -*-
"""
Created on Sun Aug 18 21:01:16 2019

@author: Dror
"""

import numpy as np

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
        return audio


class Fade(Transform):
    def __init__(self, is_in=True, duration=3):
        self.is_in = is_in
        self.duration = duration
    
    def realise(self, signal, audio):
        amp = np.linspace(0, 1, self.duration * signal.sample_rate)
        # perhaps the fade in should be nonlinear
        
        if self.is_in:
            audio[0 : self.duration*signal.sample_rate] = \
                amp*audio[0:self.duration*signal.sample_rate]
        else:
            amp = amp[::-1]
            audio[self.duration*signal.sample_rate : len(audio)-1] = \
                amp*audio[0:self.duration*signal.sample_rate]
        #return audio

class AmpFreq(Transform):
    def __init__(self, frequency, size):
        self.frequency = frequency
        self.size = size
    
    def realise(self, signal, audio):
        sin = np.sin(self.frequency * \
                     np.linspace(0, signal.duration, signal.length, False) * 2 * np.pi)
        audio[:] = audio * (sin * self.size + (1-self.size))
        #return audio
        # remember [:] is necessary to retain changes
        

class Amplitude(Transform):
    def __init__(self, size):
        self.size = size
    
    def realise(self, signal, audio):
        audio[:] = self.size * audio
        #print("realise")
        #return self.size * audio
        #audio[:] = 0.1


'''
class Mute
class Shift

+= 0.5 * Shift(5) * Fade(4) * AmpFreq(freq=10) * Sine(f)
   + 0.2 * Shift(10) * Sine(2*f)

'''













