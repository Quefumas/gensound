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
        
        if self.is_in:
            audio[0 : self.duration*signal.sample_rate] = \
                amp*audio[0:self.duration*signal.sample_rate]
        else:
            amp = amp[::-1]
            audio[self.duration*signal.sample_rate : len(audio)-1] = \
                amp*audio[0:self.duration*signal.sample_rate]

class AmpFreq(Transform):
    def __init__(self, frequency, size):
        self.frequency = frequency
        self.size = size
    
    def realise(self, signal, audio):
        sin = np.sin(self.frequency * \
                     np.linspace(0, signal.duration, signal.duration*signal.sample_rate, False) * 2 * np.pi)
        audio[:] = audio * (sin * self.size + (1-self.size))
        # remember [:] is necessary to retain changes
        

class Amplitude(Transform):
    def __init__(self, size):
        self.size = size
    
    def realise(self, signal, audio):
        audio[:] = self.size * audio

class Shift(Transform):
    """ shifts the signal forward in time.
    it is problematic to use seconds all the time,
    because of floating point numbers TODO
    """
    def __init__(self, seconds):
        self.seconds = seconds
    
    def realise(self, signal, audio):
        #signal.duration += self.seconds
        length = self.seconds*signal.sample_rate
        #length_old = audio.shape[0]
        
        
        audio2 = np.insert(audio, 0, np.zeros(self.seconds*signal.sample_rate, dtype=np.float64), axis=0)
        
        audio.resize((audio.shape[0]+length,), refcheck=False)
        audio[:] = audio2[:]
        #audio[:] = np.insert(audio, 0, np.zeros(self.seconds*signal.sample_rate, dtype=np.float64), axis=0)
        #audio[0:length], audio[length: length_old+length] = audio[length_old:length_old+length], audio[0:length_old]
    
    def on_apply(self, signal):
        signal.total_duration += self.seconds

'''

perhaps have transforms multipliable by each other to create chains,
which can then be added in bulk to a signal

the purpose is that the user can employ any order of multiplications to get
the desired result


also possible to have signal+signal automatically translate to a new track


class Mute
class Shift

+= 0.5 * Shift(5) * Fade(4) * AmpFreq(freq=10) * Sine(f)
   + 0.2 * Shift(10) * Sine(2*f)

'''













