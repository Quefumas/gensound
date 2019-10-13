# -*- coding: utf-8 -*-
"""
Created on Sat Aug 17 23:28:31 2019

@author: Dror
"""

import numpy as np

from Signal import Signal, Sine, Square, Triangle, Sawtooth, GreyNoise, WAV, Step
from transforms import Fade, AmpFreq, Shift, Channels, Pan, Extend, \
                       Downsample_rough, Average_samples, Amplitude, \
                       Reverse, Repan, Gain, Limiter, Convolution
from playback import play_WAV, play_Audio, export_WAV

from musicTheory import midC

african = "data/african_sketches_1.wav"


if __name__ == "__main__":
    #cancellation_test()
    #nonmatching_samplings()
    #convolution_test()
    after_test_3()
    #solfege_test_1()
    #db_fade_test()
    #%%%%%




















