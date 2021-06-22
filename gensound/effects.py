# -*- coding: utf-8 -*-
"""
Created on Mon Oct  5 16:46:09 2020

@author: Dror
"""

import numpy as np

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
        self.frequency = frequency
        self.width = width
    
    def realise(self, audio):
        width_samples = (2**(self.width/12) - 1)/(2*np.pi*self.frequency)*audio.sample_rate
        
        indices = np.arange(0, audio.length, 1, dtype=np.float64)
        indices += width_samples*np.sin(2*np.pi/audio.sample_rate*self.frequency * indices)
        indices[indices > audio.length-1] = audio.length - 1
        audio.audio[:,:] = audio[:, indices[:]]



