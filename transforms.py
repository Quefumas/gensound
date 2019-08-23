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
        return audio
    
    def on_apply(self, signal):
        """ when signal.apply(self) is called,
        it also calls this to allow some changes to the signal settings"""
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
                     np.linspace(0, signal.duration, signal.duration*signal.sample_rate, False) * 2 * np.pi)
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
        #signal.duration += self.seconds
        #length = self.seconds*signal.sample_rate
        #length_old = audio.shape[0]
        audio.push_forward(self.seconds * signal.sample_rate)
        
        #audio2 = np.pad(audio, ((self.seconds*signal.sample_rate,0),), mode="constant", constant_values=0.0)
        #audio.resize((audio.shape[0]+length,), refcheck=False)
        #audio[:] = audio2[:]
        #return
        
        
        #audio2 = np.insert(audio, 0, np.zeros(self.seconds*signal.sample_rate, dtype=np.float64), axis=0)
        
        #audio.resize((audio.shape[0]+length,), refcheck=False)
        #audio[:] = audio2[:]
        
        ##-------------
        #audio[:] = np.insert(audio, 0, np.zeros(self.seconds*signal.sample_rate, dtype=np.float64), axis=0)
        #audio[0:length], audio[length: length_old+length] = audio[length_old:length_old+length], audio[0:length_old]
    
    def on_apply(self, signal):
        signal.total_duration += self.seconds

class Extend(Transform):
    """ adds silence after the signal. needed?
    """
    














