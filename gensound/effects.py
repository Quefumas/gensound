# -*- coding: utf-8 -*-
"""
Created on Mon Oct  5 16:46:09 2020

@author: Dror
"""

import numpy as np

from gensound.transforms import Transform, Convolution

class OneImpulseConv(Convolution):
    def __init__(self, mix=0.5, num=1000, curve="linear"):
        if curve == "linear":
            self.response = np.linspace(mix, 0, num=num)
        elif curve == "steep":
            self.response = 1/np.linspace(1, num, num=num)
        
        self.response.resize((1, self.response.shape[0]))
        # TODO call super().__init__ instead?
        


class OneImpulseReverb(Transform):
    def __init__(self, mix=0.5, num=1000, curve="linear"):
        self.mix = mix
        self.num = num
        self.curve = curve
    
    def realise(self, audio):
        from scipy.signal import convolve
        
        # these are sensitive to sample rate!
        if self.curve == "linear":
            impulse = np.linspace(self.mix, 0, num=self.num)
        elif self.curve == "steep":
            impulse = 1/np.linspace(1, self.num, num=self.num)
        
        for i in range(audio.num_channels):
            audio.audio[i,:] = convolve(audio.audio[i,:], impulse, mode="same")
       