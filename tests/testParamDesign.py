# -*- coding: utf-8 -*-
"""
Created on Fri Mar  6 23:12:57 2020

@author: Dror
"""

import numpy as np

from musicTheory import midC
from Signal import Sine, Triangle
from transforms import Average_samples, Downsample
from curve import CompoundCurve, Curve, Constant, Line, Logistic, SineCurve
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
    c = Constant(220, 3e3) | Line(220, 330, 6e3) | Constant(330, 3e3)
    c2 = Constant(220, 2e3) | Logistic(220, midC(1), 8e3) | Constant(midC(1), 2e3)
    c3 = Constant(midC(5), 1e3) | Line(midC(5), midC(1), 9e3) | Constant(midC(1), 3e3)
    c4 = Constant(midC(14), 6e3) | Line(midC(14), midC(10), 5e3) | Constant(midC(10), 2e3)
    
    c5 = SineCurve(frequency=10, depth=0.1, baseline=330, duration=5e3)
    s = Triangle(frequency=c5, duration=12e3) * Downsample(factor=10) * Average_samples(7)
    
    audio = s.mixdown(sample_rate=11025, byte_width=2, max_amplitude=0.2)
    play_Audio(audio)
    #export_test(audio, test_glis)
    


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
    c.curves.append(Constant(3, 3e3))
    c.curves.append(Line(3, 11, 6e3))
    c.curves.append(Constant(11, 3e3))
    
    
    # x = c.flatten(4)
    # y = c.integral(4)
    # by observing y, it's not perfect
    
    
    test_glis()


























