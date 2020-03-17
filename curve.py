# -*- coding: utf-8 -*-
"""
Created on Tue Mar 10 18:34:24 2020

@author: Dror
"""

import numpy as np

from utils import num_samples, isnumber

# TODO add capabilities to adapt user-defined functions into curves on the fly
# i.e. x= Curve(lambda k: ...), then passing the lambda into flatten etc.
class Curve():
    def __init__(self, f, duration):
        self.f = f # TODO test with user-supplied f
        self.duration = duration
        
    def multi(self):
        """ converts to 1-d MultiCurve.
        """
        if isinstance(self, MultiCurve):
            return self
        
        return MultiCurve(self)
    
    def flatten(self, sample_rate):
        """ return a ndarray with the values of self for all sample points
        """
        # implemented for generic f passed into __init__, but in general this is overriden
        return np.asarray(self.f(self.sample_times(sample_rate)), dtype=np.float64)
    
    def integral(self, sample_rate):
        """ does the same as flatten, but with the cumulative sum of self
        the implementation here is catch-all, but usually much more efficient
        to override it for specific curves
        """
        vals = self.flatten(sample_rate)
        # TODO debug
        # TODO for exmple this should be divided by the durations....
        return [sum(vals[0:i]) for i in range(len(vals))]
    
    def num_samples(self, sample_rate):
        return num_samples(self.duration, sample_rate)
    
    def sample_times(self, sample_rate):
        return np.linspace(start=0, stop=self.duration/1000, num=self.num_samples(sample_rate), endpoint=False)
    
    # TODO add support for logical or as concat
    # should this be done here or at compoundcurve? imitate signal
    
    def __or__(self, other):
        c = CompoundCurve()
        
        if isinstance(self, CompoundCurve):
            c.curves += self.curves
        else:
            c.curves += [self]
        
        if isinstance(other, CompoundCurve):
            c.curves += other.curves
        else:
            c.curves += [other]
        
        return c
    

###### High-level curves #####

class CompoundCurve(Curve):
    """ A concatenation of Curves (similar to Signal/Sequence)
    """
    def __init__(self):
        self.curves = []
    
    def flatten(self, sample_rate):
        return np.concatenate([c.flatten(sample_rate) for c in self.curves])
    
    def integral(self, sample_rate):
        result = self.curves[0].integral(sample_rate)
        
        for curve in self.curves[1:]:
            result = np.concatenate((result, result[-1]+curve.integral(sample_rate)))
        
        return result
    
    def __getattr__(self, name):
        if name == "duration":
            return sum([c.duration for c in self.curves])
        raise AttributeError

class MultiCurve(Curve):
    """ Multidimensional Curve - one for each dimension (i.e. channel)
    """
    def __init__(self, *curves):
        # TODO implicitly assumes all curves of similar duration
        # will probably crash otherwise
        self.curves = curves
    
    def flatten(self, sample_rate):
        return np.asarray([[curve.flatten(sample_rate)] for curve in self.curves], dtype=np.float64)
    
    def intergral(self, sample_rate):
        return np.asarray([[curve.integral(sample_rate)] for curve in self.curves], dtype=np.float64)
    
###### Particular Curves ######

class Constant(Curve):
    def __init__(self, value, duration):
        self.value = value
        self.duration = duration
    
    def flatten(self, sample_rate):
        return np.full(shape=self.num_samples(sample_rate), fill_value=self.value)
    
    def integral(self, sample_rate):
        # TODO maybe slightly different from super.integral, due to start/end conditions
        return np.linspace(start=0, stop=self.value*self.duration/1000,
                           num=self.num_samples(sample_rate), endpoint=False)
    
class Line(Curve):
    def __init__(self, begin, end, duration):
        self.begin = begin
        self.end = end
        self.duration = duration
    
    def flatten(self, sample_rate):
        return np.linspace(start=self.begin, stop=self.end, num=self.num_samples(sample_rate), endpoint=False)
    # TODO class method of computing time ruler, or maybe length
    def integral(self, sample_rate):
        # at^/2+ bt = (at/2+b)*t
        return np.linspace(start=self.begin, stop=(self.end-self.begin)/2+self.begin,
                           num=self.num_samples(sample_rate), endpoint=False) \
            * np.linspace(start=0, stop=self.duration/1000,
                                              num=self.num_samples(sample_rate),
                                              endpoint=False)

class Logistic(Curve): # Sigmoid
    def __init__(self, begin, end, duration):
        self.begin = begin
        self.end = end
        self.duration = duration
        
        self.L = self.end - self.begin # height
        self.T = self.begin # elevation
        self.x0 = self.duration/2000 # midpoint
        self.k = 10*1000/self.duration # steepness
        # TODO parametrize steepness too
        
    
    def flatten(self, sample_rate):
        # 1 / (1 + e^(-k(x-x0)))
        time = np.linspace(start=0, stop=self.duration/1000, num=self.num_samples(sample_rate), endpoint=False)
        return self.L/(1+np.e**(-self.k*(time - self.x0))) + self.T
    
    def integral(self, sample_rate):
        # L/k * ln(1 + e^(k(x-x0))) + Tx
        # TODO faster implementation?
        time = np.linspace(start=0, stop=self.duration/1000, num=self.num_samples(sample_rate))
        return (self.L/self.k) * np.log(1 + np.e**(self.k*(time - self.x0))) + self.T * time

class SineCurve(Curve):
    def __init__(self, frequency, depth, baseline, duration):
        self.frequency = frequency
        self.depth = depth
        self.baseline = baseline
        self.duration = duration
    
    def flatten(self, sample_rate):
        return self.depth*np.sin(2*np.pi*self.frequency*self.sample_times(sample_rate)) + self.baseline
    
    def integral(self, sample_rate):
        # sin (x-pi/2) + 1
        return self.depth*np.sin(2*np.pi*self.frequency*self.sample_times(sample_rate) - np.pi/2) + self.depth + self.baseline*self.sample_times(sample_rate)
    
class Log(Curve):
    def __init__(self, max, duration, midpoint=-3):
        self.max = max
        self.duration = duration
        self.midpoint = midpoint
        self.curvature = -midpoint/np.log(2)
        assert midpoint < 0
        assert max > 0
    
    def flatten(self, sample_rate):
        return (np.log(self.sample_times(sample_rate)) - np.log(self.duration/1000))*self.curvature + self.max
    
    def integral(self, sample_rate):
        # TODO is this necessary?
        raise TypeError("Log curves should not be used as phases.")

















