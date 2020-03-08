# -*- coding: utf-8 -*-
"""
Created on Fri Mar  6 23:12:57 2020

@author: Dror
"""

import numpy as np

class Curve():
    def __init__(self):
        pass
    
    def __len__(self):
        return self.duration
    
    def iterator(self, sample_rate):
        def iterable():
            m = np.linspace(0, self.duration, round(sample_rate*self.duration/1000))
            for i in range(len(m)):
                yield self.__getitem__(m[i])
        return iterable
    
    
class Constant(Curve):
    def __init__(self, value, duration):
        self.value = value
        self.duration = duration
    
    def __getitem__(self, key): # key this should be in miliseconds
        return self.value
    
class Line(Curve):
    def __init__(self, begin, end, duration):
        self.begin = begin
        self.end = end
        self.duration = duration
    
    def __getitem__(self, key):
        return key*(self.end-self.begin)/self.duration + self.begin


class Param():
    def __init__(self):
        self.functions = [()]
    
    def __len__(self):
        pass
    
    def __getitem__(self, key):
        pass
    
    def __iter__(self):
        pass


class dummy_iter(list):
    def __init__(self, curve, rate):
        self.curve = curve
        self.rate = rate
        self.duration = curve.duration
        self.range = np.linspace(start=0, stop=self.duration, num=round(self.duration*self.rate/1000), endpoint=True)
        self.index = -1
        print(self.range.shape)
    
    def __iter__(self):
        return self
    
    def __mul__(self, other):
        return self.range*other
    
    def __next__(self):
        self.index += 1
        
        try:
            return self.curve[self.range[self.index]]
        except IndexError:
            self.index = 0
            raise StopIteration
    
    __array_priority__ = 10000

if __name__ == "__main__":
#    z = np.linspace(0, 1, 400)
#    x = Line(1, 15, 4e3)
#    z *= x.iterator(100)
    
    a = Line(1, 15, 4e3)
    t = []
    for i in dummy_iter(a, 10):
        t += [i]
#    b = np.ones(shape=(1,40))
#    b = dummy_iter(a, 10)*b
#    b = b*range(1,41)



























