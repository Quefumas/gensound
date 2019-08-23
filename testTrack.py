# -*- coding: utf-8 -*-
"""
Created on Sat Aug 17 23:28:31 2019

@author: Dror
"""

import simpleaudio as sa

from Signal import Sine, Square, Triangle, Sawtooth, GreyNoise
from transforms import Fade, AmpFreq, Shift


def only_signal_harmonics(f=220, seconds=5):
    params = [(0.34, 1, 2, 0.45),
              (0.2, 1.94, 3, 0.7),
              (0.2, 3, 2.3, 0.3),
              (0.15, 3.9994, 2.1, 0.67),
              (0.19, 5.1, 0.8, 0.46),
              (0.12, 5.96, 1.3, 0.34),
              (1/7, 7, 1.2, 0.5),
              (0.119, 8.1, 2.9, 0.23),
              (0.2, 9, 1.3, 0.4),
              (1/10, 9.87, 0.65, 0.4),
              ]
    
    t = sum([p[0]*Triangle(frequency=f*p[1], duration=seconds)*\
             Fade(is_in=True, duration=3)*\
             AmpFreq(frequency=p[2], size=p[3])*\
             Shift(seconds=1) for p in params])
    
    return t.mixdown()

def simple_test(f=220, seconds=5):
    t = Sine(frequency=230)*AmpFreq(frequency=1, size=0.2) + \
        Square(frequency=300)*AmpFreq(frequency=0.7, size=0.6)
    t *= Fade(is_in=True, duration=3)
    t *= Shift(seconds=1)
    return t.mixdown()

if __name__ == "__main__":
    
    
    audio = simple_test()
    #%%%%%
    play_obj = sa.play_buffer(audio, num_channels=1, bytes_per_sample=2, sample_rate=11025)
    play_obj.wait_done()
    
    
    #play_obj = sa.play_buffer(audio, num_channels=2, bytes_per_sample=2, sample_rate=11025)
    
    #c = input("Type something to quit.")
    #play_obj.stop()
    #play_obj.wait_done()




