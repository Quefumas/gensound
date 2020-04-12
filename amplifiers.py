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
    Sample response is 1/(1+e^(-harshness*x) - 0.5
    
    Limit affects the maximum amplitude achievable (should be lower than maximum
    amplitude in input signal), and harshness the steepness.
    
    Cutoff is for the low-pass applied later to simulate the cabinet.
    """
    def __init__(self, harshness, cutoff=5000, asymmetric=True):
        assert harshness > 0
        self.harshness = harshness
        self.cutoff = cutoff
        self.asymmetric = asymmetric
    
    def realise(self, audio):
        
        # max_amp = self # refactor so that it can reach theo riginal amplitude level
        # now try with asymmetric clipping, hard on the negative and soft on the positives
        test = "soft-soft"
        if test == "soft-hard":
            audio.audio[audio.audio>1] = 1
            negs = audio.audio < -1
            audio.audio[negs] *= (2-np.abs(audio.audio[negs]))
        elif test == "soft-soft":
            audio.audio[audio.audio>1] = 1
            audio.audio[audio.audio<-1] = -1
            mid = (audio.audio > -1) & (audio.audio < 1)
            audio.audio[mid] *= (2-np.abs(audio.audio[mid]))
        elif self.asymmetric:
            #limit = 1/(1+np.e**(-self.harshness)) - 0.5
            limit = 0.5
            positives = audio.audio > 0
            neg_clips = audio.audio < -limit
            audio.audio[positives] = (1/(1+np.e**(-self.harshness*audio.audio[positives])) - 0.5)
            audio.audio[neg_clips] = -limit
        else:
            audio.audio[:,:] = (1/(1+np.e**(-self.harshness*audio.audio)) - 0.5)
        
        lowpass = IIR_OnePole_LowPass(cutoff=self.cutoff)
        lowpass.realise(audio)
        # TODO add cutoff



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
        













