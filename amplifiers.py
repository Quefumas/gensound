# -*- coding: utf-8 -*-
"""
Created on Sat Apr 11 13:32:27 2020

@author: Dror
"""

import numpy as np
from transforms import Transform
from filters import IIR_OnePole_LowPass

class GuitarAmp_Test(Transform):
    """ Works by applying a sigmoid to the signal, squashing it somewhat
    violently.
    Sample response is limit / (1/(1+e^(-harshness*x) - 0.5)
    
    Limit affects the maximum amplitude achievable (should be lower than maximum
    amplitude in input signal), and harshness the steepness.
    
    Cutoff is for the low-pass applied later to simulate the cabinet.
    """
    def __init__(self, harshness, cutoff=5000):
        assert harshness > 0
        self.harshness = harshness
        self.cutoff = cutoff
    
    def realise(self, audio):
        
        # max_amp = self # refactor so that it can reach theo riginal amplitude level
        audio.audio[:,:] = (1/(1+np.e**(-self.harshness*audio.audio)) - 0.5)
        
        lowpass = IIR_OnePole_LowPass(cutoff=self.cutoff)
        lowpass.realise(audio)
        # TODO add cutoff