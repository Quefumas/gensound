# -*- coding: utf-8 -*-
"""
Created on Thu Sep  5 19:04:56 2019

@author: Dror
"""

import numpy as np
from audio import Audio

def RMS(audio, start, end):
    return (np.sum(audio.audio[:,start:end]**2) / (audio.num_channels*(end-start)))**0.5


def DFT(audio, N, start=0):
    # TODO only supports mono
    
    return [(sum([audio.audio[0, start+n]*np.cos(2*np.pi*n*m/N) for n in range(0,N)]),
    -sum([audio.audio[0, start+n]*np.sin(2*np.pi*n*m/N) for n in range(0,N)])) for m in range(0,N)]
    
