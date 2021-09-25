# -*- coding: utf-8 -*-

import numpy as np

from gensound.settings import _supported
from gensound.curve import Curve, Line, Logistic, Constant
from gensound.transforms import Transform
from gensound.utils import lambda_to_range, DB_to_Linear, \
                  isnumber, iscallable, \
                  num_samples, samples_slice

# TODO top-class FIR/IIR/Filter?
# that could include a useful function for debugging that generates the impulse response


######## FIRs


class Filter:
    def plot_frequency_response(self, sample_rate=44100):
        assert "matplotlib" in _supported, "matplotlib missing, plot_frequency_response not available."
        from gensound.visualise import _plot_frequency_response
        _plot_frequency_response(self, sample_rate)
        
        


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
    



############ IIRs

class IIR(Transform, Filter):
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
    
    def _realise_scipy(self, audio):
        b, a = self.coefficients(audio.sample_rate)
        assert len(b) == len(a), "Please supply to IIR same number of feedforward and feedback coefficients"
        
        from scipy.signal import lfilter
        audio.audio[:,:] = lfilter(b, a, audio.audio)
    
    def _realise_native(self, audio):
        b, a = self.coefficients(audio.sample_rate)
        assert len(b) == len(a), "Please supply to IIR same number of feedforward and feedback coefficients"
        
        y = np.zeros((audio.num_channels, audio.length + len(a) + len(b)))
        parallel = np.zeros((len(b), audio.num_channels, audio.length+len(b)-1))
        
        for i in range(len(b)):
            parallel[i, :, i:audio.length+i] = b[i]*audio.audio
        
        y[:,:parallel.shape[2]] = np.sum(parallel, axis=0)[:,:] # feedforward
        
        for i in range(0, y.shape[1]-len(a)+1): # feedback
            for m in range(1, len(a)):
                y[:,i] -= a[m]*y[:,i-m]
        
        audio.audio[:,:] = y[:,:audio.length]
    
    if "scipy" in _supported:
        realise = _realise_scipy
    else:
        realise = _realise_native
        

class SimpleLPF(IIR):
    """
    McPherson
    """
    def __init__(self, cutoff):
        self.cutoff = cutoff
    
    def coefficients(self, sample_rate):
        Fc = 2*np.pi * self.cutoff / sample_rate
        
        # can also simplify instead of using beta
        beta = (1 - np.tan(Fc/2)) / (1 + np.tan(Fc/2))
        
        a = (1, -beta)
        b = ((1-beta)/2, (1-beta)/2)
        return (b, a)


class SimpleHPF(IIR):
    """
    McPherson
    """
    def __init__(self, cutoff):
        self.cutoff = cutoff
    
    def coefficients(self, sample_rate):
        Fc = 2*np.pi * self.cutoff / sample_rate
        
        beta = (1 - np.tan(Fc/2)) / (1 + np.tan(Fc/2))
        
        a = (1, -beta)
        b = ((1+beta)/2, -(1+beta)/2)
        return (b, a)



class SimpleLowShelf(IIR):
    """
    McPherson
    """
    def __init__(self, cutoff, gain=None, dB=None):
        assert (gain is None) + (dB is None) == 1, "SimpleLowShelf requires specifying exactly one of 'gain' and 'dB'."
        self.cutoff = cutoff
        self.gain = DB_to_Linear(dB) if gain is None else gain
    
    def coefficients(self, sample_rate):
        Fc = 2*np.pi * self.cutoff / sample_rate
        
        beta = (1 - np.tan(Fc/2)) / (1 + np.tan(Fc/2))
        
        a = (1, -beta)
        b = ((1 + self.gain + (1-self.gain)*beta)/2, -(1 - self.gain + (1+self.gain)*beta)/2)
        return (b, a)



class SimpleHighShelf(IIR):
    """
    McPherson
    """
    def __init__(self, cutoff, gain=None, dB=None):
        assert (gain is None) + (dB is None) == 1, "SimpleHighShelf requires specifying exactly one of 'gain' and 'dB'."
        self.cutoff = cutoff
        self.gain = DB_to_Linear(dB) if gain is None else gain
    
    def coefficients(self, sample_rate):
        Fc = 2*np.pi * self.cutoff / sample_rate
        
        beta = (1 - np.tan(Fc/2)) / (1 + np.tan(Fc/2))
        
        a = (1, -beta)
        b = ((1 + self.gain + (self.gain-1)*beta)/2, (1 - self.gain - (1+self.gain)*beta)/2)
        return (b, a)




class SimpleBandPass(IIR):
    def __init__(self, lower, upper):
        self.lower = lower
        self.upper = upper
    
    def coefficients(self, sample_rate):
        B = 2*np.pi*(self.upper - self.lower) / sample_rate
        Fc = 2*np.pi*(self.lower + self.upper) /2 / sample_rate
        
        b = (np.tan(B/2), 0, -np.tan(B/2))
        a = (1 + np.tan(B/2), -2*np.cos(Fc), 1-np.tan(B/2))
        
        b = [c/a[0] for c in b]
        a = [c/a[0] for c in a]
        
        return (b, a)




class SimpleBandStop(IIR):
    def __init__(self, lower, upper):
        self.lower = lower
        self.upper = upper
    
    def coefficients(self, sample_rate):
        B = 2*np.pi*(self.upper - self.lower) / sample_rate
        Fc = 2*np.pi*(self.lower + self.upper) /2 / sample_rate
        
        b = (1, -2*np.cos(Fc), 1)
        a = (1 + np.tan(B/2), -2*np.cos(Fc), 1-np.tan(B/2))
        
        b = [c/a[0] for c in b]
        a = [c/a[0] for c in a]
        
        return (b, a)



class SimpleNotch(IIR):
    def __init__(self, lower, upper, gain=None, dB=None):
        assert (gain is None) + (dB is None) == 1, "SimpleNotch requires specifying exactly one of 'gain' and 'dB'."
        self.lower = lower
        self.upper = upper
        self.gain = DB_to_Linear(dB) if gain is None else gain
    
    def coefficients(self, sample_rate):
        B = 2*np.pi*(self.upper - self.lower) / sample_rate
        Fc = 2*np.pi*(self.lower + self.upper) /2 / sample_rate
        
        b = (1 + self.gain*np.tan(B/2), -2*np.cos(Fc), 1 - self.gain*np.tan(B/2))
        a = (1 + np.tan(B/2), -2*np.cos(Fc), 1-np.tan(B/2))
        
        b = [c/a[0] for c in b]
        a = [c/a[0] for c in a]
        
        return (b, a)







#### SciPy.Signal ####

class ButterworthLowPass(IIR):
    def __init__(self, cutoff, order):
        """ cutoff - the cutoff frequency (Hz)
        order - the order of the filter (1 or more)
        The higher the order, the stronger the filtering.
        """
        assert "scipy" in _supported, "SciPy required for Butterworth"
        self.cutoff = cutoff
        self.order = order
    
    def coefficients(self, sample_rate):
        from scipy.signal import butter
        return butter(self.order, [self.cutoff/sample_rate*2], btype='lowpass', output='ba')


class ButterworthHighPass(IIR):
    def __init__(self, cutoff, order):
        """ cutoff - the cutoff frequency (Hz)
        order - the order of the filter (1 or more)
        The higher the order, the stronger the filtering.
        """
        assert "scipy" in _supported, "SciPy required for Butterworth"
        self.cutoff = cutoff
        self.order = order
    
    def coefficients(self, sample_rate):
        from scipy.signal import butter
        return butter(self.order, [self.cutoff/sample_rate*2], btype='highpass', output='ba')
    
class ButterworthBandPass(IIR):
    def __init__(self, lower, upper, order):
        """ lower, upper - the range of frequencies that will remain.
        order - the order of the filter (2 or more)
        The higher the order, the stronger the filtering.
        """
        assert "scipy" in _supported, "SciPy required for Butterworth"
        self.lower = lower
        self.upper = upper
        self.order = order
    
    def coefficients(self, sample_rate):
        from scipy.signal import butter
        return butter(self.order, [self.lower/sample_rate*2, self.upper/sample_rate*2], btype='bandpass', output='ba')


class ButterworthBandStop(IIR):
    def __init__(self, lower, upper, order):
        """ lower, upper - the range of frequencies that will be blocked.
        order - the order of the filter (2 or more)
        The higher the order, the stronger the filtering.
        """
        assert "scipy" in _supported, "SciPy required for Butterworth"
        self.lower = lower
        self.upper = upper
        self.order = order
    
    def coefficients(self, sample_rate):
        from scipy.signal import butter
        return butter(self.order, [self.lower/sample_rate*2, self.upper/sample_rate*2], btype='bandstop', output='ba')









