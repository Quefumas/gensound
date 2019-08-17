# -*- coding: utf-8 -*-
"""
Created on Sat Aug 17 23:28:31 2019

@author: Dror
"""

import numpy as np
import simpleaudio as sa

from Track import Track
from Signal import Sine

if __name__ == "__main__":
    t = Track()
    t.append(signal=Sine(frequency=220, duration=5), time=1)
    t.append(signal=Sine(frequency=330, duration=4), time=2)
    
    audio = t.realise()
    
    play_obj = sa.play_buffer(audio, num_channels=1, bytes_per_sample=2, sample_rate=11025)
    
    #c = input("Type something to quit.")
    #play_obj.stop()
    play_obj.wait_done()




