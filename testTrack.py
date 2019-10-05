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

def cancellation_test():
    #signal = Sine(duration=5000) - 0.999*Sine(duration=5000)
    #signal += 0.01*Sine(frequency=130,duration=1000)
    signal = WAV(african) - WAV(african)*Repan((1,0))
    #signal += 0.5*WAV(african) # basically neautralized the center "channel"
    #signal += 5.0*WAV(african) # strengthens center
    
    audio = signal.mixdown(sample_rate=44100, byte_width=2, max_amplitude=0.2)
    play_Audio(audio, is_wait=True)

def nonmatching_samplings():
    signal = WAV(african) # its the users responsibility to know the sample rates
    audio = signal.mixdown(sample_rate=32000, byte_width=2, max_amplitude=0.2)
    # 8k, 11025, 16k, 22050, 24k, 32k, 44.1k, 48k, 88.2k, 96k, 192k
    play_Audio(audio, is_wait=True)

def convolution_test():
    signal = WAV(african)*Convolution(forward=False, add=0.3, is_both_ways=False)*Average_samples(11)
    signal -= 0.1*WAV(african)
    audio = signal.mixdown(sample_rate=44100, byte_width=2, max_amplitude=0.2)
    play_Audio(audio, is_wait=True)

def after_test_1():
    signal = Sine(frequency=midC(-7), duration=6e3)
    s2 = Signal.concat(*[Sine(frequency=midC(k-4), duration=1e3) for k in range(6)])
    signal += s2
    
    print(signal)
    audio = signal.mixdown(sample_rate=44100, byte_width=2, max_amplitude=0.2)
    play_Audio(audio, is_wait=True)

if __name__ == "__main__":
    #cancellation_test()
    #nonmatching_samplings()
    #convolution_test()
    after_test_1()
    #%%%%%




















