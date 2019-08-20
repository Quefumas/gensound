# -*- coding: utf-8 -*-
"""
Created on Sat Aug 17 23:28:31 2019

@author: Dror
"""

import numpy as np
import simpleaudio as sa

from Track import Track
from Signal import Sine
from transforms import Fade, AmpFreq, Amplitude

if __name__ == "__main__":
    t = Track()
    
    f = 220
    seconds = 10
    
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
    
    for p in params:
        s = Sine(frequency=f*p[1], duration=seconds)
        s.apply(Amplitude(size = p[0]))
        s.apply(Fade(is_in=True, duration=3))
        s.apply(AmpFreq(frequency=p[2], size=p[3]))
        #pass
        t.append(s, time=1)
    
    #s = Sine(frequency=220, duration=5)
    #s.apply(Fade(is_in=True, duration=5))
    #s.apply(Amplitude(size=0.3))
    #s.apply(AmpFreq(frequency=2, size=0.3))
    #t.append(s, time=1)
    
    
    #s2= Sine(frequency=400, duration=5)
    #s2.apply(Fade(is_in=True, duration=5))
    #s2.apply(Amplitude(size=0.1))
    #s2.apply(AmpFreq(frequency=2, size=0.3))
    #t.append(s2, time=1)
    
    audio = t.realise()
    
    #%%%%%
    play_obj = sa.play_buffer(audio, num_channels=1, bytes_per_sample=2, sample_rate=11025)
    
    #c = input("Type something to quit.")
    #play_obj.stop()
    play_obj.wait_done()




