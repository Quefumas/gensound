# -*- coding: utf-8 -*-
"""
Created on Fri Sep  6 01:04:28 2019

@author: Dror
"""

import numpy as np
import simpleaudio as sa

def test_click():
    
    buffer = np.zeros((11025*4,), dtype=np.int16)
    buffer[11025:22050] = 32000
    buffer[33075:44000] = 32000
    
    play_obj = sa.play_buffer(buffer,
                              num_channels=1,
                              bytes_per_sample=2, # TODO should Audio store this?
                              sample_rate=11025)
    
    play_obj.wait_done()


if __name__ == "__main__":
    test_click()