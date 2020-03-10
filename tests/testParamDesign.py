# -*- coding: utf-8 -*-
"""
Created on Fri Mar  6 23:12:57 2020

@author: Dror
"""

import numpy as np

from utils import samples
from Signal import Sine
from curve import CompoundCurve, Curve, Constant, Line
from playback import play_WAV, play_Audio, export_test

############ ---------------

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

####################################
    
def test_glis():
    c = CompoundCurve()
    c.curves.append(Constant(220, 6e3))
    c.curves.append(Line(220, 330, 9e3))
    c.curves.append(Constant(330, 3e3))
    
    s = Sine(frequency=c, duration=18e3)
    # TODO duration shouldn't be releveant if frequency is a curve
    # in that case it should be computed inside Signal.__init__ on its own
    audio = s.mixdown(sample_rate=11025, byte_width=2, max_amplitude=0.2)
    #play_Audio(audio)
    export_test(audio, test_glis)
    


if __name__ == "__main__":
#    z = np.linspace(0, 1, 400)
#    x = Line(1, 15, 4e3)
#    z *= x.iterator(100)
    
    # a = Line(1, 15, 4e3)
    # t = []
    # for i in dummy_iter(a, 10):
    #     t += [i]
#    b = np.ones(shape=(1,40))
#    b = dummy_iter(a, 10)*b
#    b = b*range(1,41)
    #######
    c = CompoundCurve()
    c.curves.append(Constant(3, 6e3))
    c.curves.append(Line(3, 11, 9e3))
    c.curves.append(Constant(11, 3e3))
    
    # x = c.flatten(4)
    # y = c.integral(4)
    # by observing y, it's not perfect
    
    
    test_glis()


























