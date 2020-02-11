# -*- coding: utf-8 -*-
"""
Created on Sat Aug 17 23:28:31 2019

@author: Dror
"""

import numpy as np

from Signal import Signal, Sine, Square, Triangle, Sawtooth, GreyNoise, WAV, Step
from transforms import Fade, AmpFreq, Shift, Channels, Pan, Extend, \
                       Downsample_rough, Average_samples, Amplitude, \
                       Reverse, Repan, Gain, Limiter, Convolution, Slice
from playback import play_WAV, play_Audio, export_test # better than export_WAV for debugging

from musicTheory import midC

african = "data/african_sketches_1.wav"


def slice_test():
    hihat = WAV(african)[:1061]*Average_samples(5)
    hihat **= 30
    
    part = WAV(african)[5*1061:5*1061+3*1061]
    part**=20
    s = WAV(african) + part*Shift(4*1061)*Gain(-6) - hihat
    #s = hihat
    audio = s.mixdown(sample_rate=32000, byte_width=2, max_amplitude=0.2)
    #play_Audio(audio)
    export_test(audio, slice_test)

def slice_set_test():
    s = WAV(african)
    # careful with 5e3, creates float slices
    
    #s[5e3:18e3] = s[5e3:18e3]*Repan() + s[5e3:18e3]*Downsample_rough(5)*Gain(-3)
    #s[5e3:18e3] *= Repan(1,0)
    s[5e3:18e3] = s[5e3:18e3]*Repan(1 ,None) + s[5e3:18e3]*Repan(None, 0)
    # TODO found a bug here? does it really keep both copies of the slice separate?
    # also test s = s[0:50] & sine() & s[50:100]
    
    audio = s.mixdown(sample_rate=44100, byte_width=2, max_amplitude=0.2)
    play_Audio(audio)
    #export_test(audio, slice_set_test)

def concat_overload_test():
    #s = Sine(frequency=250, duration=2e3) | Triangle(frequency=300, duration=3e3)
    s = WAV(african)
    
    s = s[5e3:5.5e3] | s[6e3:6.8e3] | s[11e3:13e3]*Reverse()+Sine(frequency=300, duration=2e3) | s[9e3:10.8e3]
    
    audio = s.mixdown(sample_rate=44100, byte_width=2, max_amplitude=0.2)
    play_Audio(audio)
    #export_test(audio, concat_overload_test)

def messy_random_concat_test():
    s = WAV(african)
    
    max_length = 20e3
    
    def messy_track():
        t = 0
        temp = 0
        
        while temp < max_length:
            duration = 400 + np.random.random()*3e3
            temp += duration
            start = 4e3 + (30-4)*np.random.random()*1e3
            t |= s[start:start+duration]
        
        return t
    
    
    L = messy_track() + messy_track()
    R = messy_track() + messy_track()
    
    s = L*Repan(0, None) + R*Repan(None, 1)
    
    t = sum([(1-8/10)*s*Shift(duration=100*x)*Average_samples(weights=2*x+1) for x in range(5)])
    t += 0.6*s*Downsample_rough(factor=5)*Average_samples(weights=5)
    
    audio = t.mixdown(sample_rate=44100, byte_width=2, max_amplitude=0.2)
    play_Audio(audio)
    #export_test(audio, messy_random_concat_test)
    
def concat_scalar_test():
    s = WAV(african)
    
    gap = 0.1
    L = s[10e3:11e3] | gap | s[11e3:12e3] | gap | s[12e3:13e3] | gap | s[13e3:14e3] \
        | gap | s[14e3:15e3] | gap | s[15e3:16e3] | gap | s[16e3:17e3]
    R = s[10e3:17e3]
    
    s = L*Repan(0, None) + R*Repan(None, 1)
    
    audio = s.mixdown(sample_rate=44100, byte_width=2, max_amplitude=0.2)
    #play_Audio(audio)
    export_test(audio, concat_scalar_test)
    # this is a funky effect of panning by dephasing...

if __name__ == "__main__":
    concat_scalar_test()
    
    
    
    #%%%%%




















