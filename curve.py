# -*- coding: utf-8 -*-
"""
Created on Tue Mar 10 18:34:24 2020

@author: Dror
"""

import numpy as np

from utils import samples

class Curve():
    def __init__(self):
        pass
    
    def flatten(self, sample_rate):
        """ return a ndarray with the values of self for all sample points
        """
        pass
    
    def integral(self, sample_rate):
        """ does the same as flatten, but with the cumulative sum of self
        the implementation here is catch-all, but usually much more efficient
        to override it for specific curves
        """
        vals = self.flatten(sample_rate)
        return [sum(vals[0:i]) for i in range(len(vals))]
    
    
class Constant(Curve):
    def __init__(self, value, duration):
        self.value = value
        self.duration = duration
    
    def flatten(self, sample_rate):
        return np.full(shape=samples(self.duration, sample_rate), fill_value=self.value)
    
    def integral(self, sample_rate):
        # TODO maybe slightly different from super.integral, due to start/end conditions
        return np.linspace(start=0, stop=self.value*self.duration/1000,
                           num=samples(self.duration, sample_rate), endpoint=False)
    
class Line(Curve):
    def __init__(self, begin, end, duration):
        self.begin = begin
        self.end = end
        self.duration = duration
    
    def flatten(self, sample_rate):
        return np.linspace(start=self.begin, stop=self.end, num=samples(self.duration, sample_rate), endpoint=False)
    
    def integral(self, sample_rate):
        # at^/2+ bt = (at/2+b)*t
        return np.linspace(start=self.begin, stop=(self.end-self.begin)/2+self.begin,
                           num=samples(self.duration, sample_rate), endpoint=False) \
            * np.linspace(start=0, stop=self.duration/1000,
                                              num=(samples(self.duration, sample_rate)),
                                              endpoint=False)


class CompoundCurve(Curve):
    def __init__(self):
        self.curves = []
    
    def flatten(self, sample_rate):
        return np.concatenate([c.flatten(sample_rate) for c in self.curves])
    
    def integral(self, sample_rate):
        result = self.curves[0].integral(sample_rate)
        
        for curve in self.curves[1:]:
            result = np.concatenate((result, result[-1]+curve.integral(sample_rate)))
        
        return result
        
