# -*- coding: utf-8 -*-
"""
Created on Wed Mar 25 15:42:08 2020

@author: Dror
"""

import numpy as np
from gensound.curve import Curve, Line, Logistic, Constant
from gensound.audio import Audio
from gensound.transforms import Transform
from gensound.utils import lambda_to_range, DB_to_Linear, \
                  isnumber, iscallable, \
                  num_samples, samples_slice

# TODO top-class FIR/IIR/Filter?
# that could include a useful function for debugging that generates the impulse response


######## FIRs

class FIR(Transform):
    """ Implements a general-purpose FIR. Subclasses of this can deal solely with
    computing the desired coefficients by overriding FIR.coefficients,
    leaving the actual application to FIR.realise.
    The implementation here may change in the future, and is not guaranteed to be optimal.
    Possibly several alternative implementations will be included, for learning,
    testing and reference purposes. If more competitive implementation is required,
    it is easy enough to extend.
    """
    def __init__(self, *coefficients): # can override this if coefficients are independent of sample rate
        total = sum(coefficients)
        self.h = [c/total for c in coefficients]
        
    def coefficients(self, sample_rate): # override here if sample rate is needed
        # and just ignore the arguments for init
        return self.h
    
    def _parallel_copies(self, audio):
        """ Makes |h| copies of audio, shifting each by the proper amount
        and multiplying by the appropriate coefficient, then summing.
        """
        h = self.coefficients(audio.sample_rate)
        n = audio.length
        parallel = np.zeros((len(h), audio.num_channels, n+len(h)-1), dtype=np.float64)
        
        for i in range(len(h)):
            parallel[i,:,i:n+i] = h[i]*audio.audio
            
        audio.audio[:,:] = np.sum(parallel, axis=0)[:,:n] # TODO trims the end, how to handle this
    
    def _standing_sum(self, audio):
        """ Sums scaled copies of audio into a single ndarray.
        """
        h = self.coefficients(audio.sample_rate)
        new_audio = np.zeros_like((audio.num_channels, audio.length+len(h)-1))
        # could technically skip this first step
        
        for i in range(len(h)):
            new_audio[:,i:audio.length+i] += h[i]*audio.audio
        
        audio.audio[:,:] = new_audio[:,:audio.length] # trims the tail
    
    def realise(self, audio): # override if you have a particular implementation in mind
        self._parallel_copies(audio)
    
    # TODO maybe add class method to facilitate diagnosis of FIR, frequency/phase responses etc.

class MovingAverage(FIR):
    """ Averager Low Pass FIR, oblivious to sample rate.
    """
    def __init__(self, width):
        self.h = [1/width]*width
    

class LowPassBasic(Transform): # TODO I hear a band pass, and a lousy one too
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
        n = audio.length
        parallel = np.zeros((len(h), audio.num_channels, audio.length+len(h)-1), dtype=np.float64)
        for i in range(len(h)):
            parallel[i,:,i:n+i] = h[i]*audio.audio
            
        audio.audio[:,:] = np.sum(parallel, axis=0)[:,:n]


class Butterworth(Transform): # LowPass FIR
    def __init__(self, cutoff):
        self.cutoff = cutoff
    
    def realise(self, audio):
        from scipy.signal import butter,filtfilt
        order = 2
        
        normal_cutoff = self.cutoff*2 / audio.sample_rate
        b, a = butter(order, normal_cutoff, btype='low', analog=False)
        audio.audio[:,:] = filtfilt(b, a, audio.audio)


############ IIRs

class IIR(Transform):
    """ General-purpose IIR implementation. Subclasses can deal solely with coefficient selection,
    without worrying about the implementation. Override __init__ or coefficients,
    depending on whether or not the sample rate is relevant (typically is).
    """
    def __init__(self, feedforward, feedback): # override this if coefficients are independent of sample rate
        """ Expects two iterables. Feedback[0] is typically 1."""
        self.b = [c/feedback[0] for c in feedforward]
        self.a = [c/feedback[0] for c in feedback]
    
    def coefficients(self, sample_rate): # override this if sample rate is needed
        return (self.b, self.a)
    
    def realise(self, audio): # naive implementation
        # TODO at least the feed-forward coefficients can be computed en masse
        b, a = self.coefficients(audio.sample_rate)
        x = np.pad(audio.audio, ((0,0),(len(a)-1,0))) # max(len(a),len(b))-1
        y = np.zeros_like(x)
        
        for i in range(len(a), x.shape[1]):
            for n in range(len(b)):
                y[:,i] += b[n]*x[:,i-n]
                
            for m in range(1, len(a)):
                y[:,i] -= a[m]*y[:,i-m]
        
        audio.audio[:,:] = y[:,:audio.length]

class OnePoleLPF(IIR):
    """ Designed after Nigel Redmond.
    https://www.earlevel.com/main/2012/12/15/a-one-pole-filter/
    
    For low pass, with Fc being cutoff/sample_rate,
    use b1 = e^{-2 pi Fc}
    and a0 = 1-b1
    
    6dB/octave
    """
    def __init__(self, cutoff):
        self.cutoff = cutoff
    
    def coefficients(self, sample_rate):
        Fc = self.cutoff / sample_rate
        a = (1, -np.e**(-2*np.pi*Fc))
        b = (1 - a[1], )
        return (b, a)


class OnePoleHPF(IIR):
    """ Designed after Nigel Redmond.
    https://www.earlevel.com/main/2012/12/15/a-one-pole-filter/
    
    Not very effective for not very high cutoffs.
    
    b1 = - e^{-2 pi (0.5-Fc)}
    a0 = 1+b1
    
    6dB/octave
    """
    def __init__(self, cutoff):
        self.cutoff = cutoff
    
    def coefficients(self, sample_rate):
        Fc = self.cutoff / sample_rate
        a = (1, np.e**(-2*np.pi*(0.5-Fc)))
        b = (1 + a[1], )
        return (b, a)












