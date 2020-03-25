# -*- coding: utf-8 -*-
"""
Created on Wed Mar 25 15:42:08 2020

@author: Dror
"""

import numpy as np
from curve import Curve, Line, Logistic, Constant
from audio import Audio
from transforms import Transform
from utils import lambda_to_range, DB_to_Linear, \
                  isnumber, iscallable, \
                  num_samples, samples_slice

class Average_samples(Transform):
    """ averages each sample with its neighbors, possible to specify weights as well.
    effectively functions as a low pass filter, without the aliasing effects
    of downsample rough.
    """
    
    def __init__(self, *weights):
        """
        weights is int -> average #weights neighboring samples
        weights is tuple -> average len(weights) neighboring samples,
                            according to specified weights. will be normalized to 1.
        TODO: on the edges this causes a small fade in fade out of length len(weights).
        not necessarily a bug though.
        """
        if len(weights) == 1:
            weights = tuple(1 for w in range(weights[0]))
        
        total = sum(weights)
        weights = [w/total for w in weights]
        self.weights = weights
    
    def realise(self, audio):
        res = np.zeros((audio.audio.shape[0], audio.audio.shape[1] + len(self.weights) - 1), dtype=np.float64)
        
        for i, weight in enumerate(self.weights):
            res[:,i:audio.audio.shape[1]+i] += weight*audio.audio
        
        pos = int(np.floor((len(self.weights) - 1)/2))
        # the index from which to start reading the averaged signal
        # (as it is longer due to time delays)
        
        audio.audio[:,:] = res[:, pos:pos+audio.audio.shape[1]]


class LowPassBasic(Transform):
    def __init__(self, cutoff, width):
        self.cutoff = cutoff
        self.width = width # number of samples in FIR
    
    def coefficients(self, sample_rate):
        n = np.linspace(start=-self.width/2, stop=self.width/2, num=self.width+1, endpoint=True)
        omega = 2*np.pi*self.cutoff/sample_rate
        h = np.sin(omega*n)/np.pi/n
        h[int(self.width/2)] = omega/np.pi
        
        
        blackman = [ 0.42 - 0.5*np.cos(2*np.pi*k/(self.width-1)) + 0.08*np.cos(4*np.pi*k/(self.width-1)) for k in range(self.width)]
        
        return h*n
    
    def realise2(self, audio):
        h = self.coefficients(audio.sample_rate)[::-1] # its symmetric tho
        
        res = np.zeros_like(audio.audio, dtype=np.float64)        
        padded = np.pad(audio.audio, ((0,0),(len(h)-1,0)))
        
        for i in range(audio.audio.shape[1]):
            #TODO faster
            res[:,i] = np.sum(h*padded[:,i:i+len(h)], axis=1)
        
        assert res.shape == audio.audio.shape, "FIR distorted audio shape!"
        audio.audio[:,:] = res
    
    def realise(self, audio):
        h = self.coefficients(audio.sample_rate)#[::-1] # its symmetric tho
        n = audio.length()
        parallel = np.zeros((len(h), audio.num_channels(), audio.length()+len(h)-1), dtype=np.float64)
        for i in range(len(h)):
            parallel[i,:,i:n+i] = h[i]*audio.audio
            
        audio.audio[:,:] = np.sum(parallel, axis=0)[:,:n]


class Butterworth(Transform):
    def __init__(self, cutoff):
        self.cutoff = cutoff
    
    def realise(self, audio):
        from scipy.signal import butter,filtfilt
        order = 2
        
        normal_cutoff = self.cutoff*2 / audio.sample_rate
        b, a = butter(order, normal_cutoff, btype='low', analog=False)
        audio.audio[:,:] = filtfilt(b, a, audio.audio)

