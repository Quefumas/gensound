# -*- coding: utf-8 -*-
"""
Created on Sat Aug 17 23:28:31 2019

@author: Dror
"""

import numpy as np

from Signal import Signal, Sine, Square, Triangle, Sawtooth, GreyNoise, WAV, Step
from transforms import Fade, AmpFreq, Shift, Pan, Extend, \
                       Downsample_rough, Amplitude, \
                       Reverse, Repan, Gain, Limiter, Convolution, Slice, \
                       Mono, ADSR
from filters import Average_samples, LowPassBasic, Butterworth
from curve import Curve, Constant, Line, Logistic, SineCurve
from playback import play_WAV, play_Audio, export_test # better than export_WAV for debugging

from musicTheory import midC

african = "../data/african_sketches_1.wav"


def curve_continuity_test():
    c = Line(220,330,4e3) | Constant(330, 4e3)
    s = Sine(frequency=c, duration=8e3)
    
    c2 = Constant(220, 2e3) | Line(220, 330, 9e3) | Constant(330, 2e3)
    s = Sine(frequency=c2, duration=18e3)
    audio = s.mixdown(sample_rate=11025, byte_width=2, max_amplitude=0.2)
    play_Audio(audio)
    #export_test(audio, curve_continuity_test)

def to_infinity_curve_test():
    c = Line(-80,-10,10e3)
    p = Line(-100, 100, 5e3)
    #s = Sine(duration=20e3)*Gain(c)
    s = Sine(duration=10e3)*Pan(p)
    audio = s.mixdown(sample_rate=11025, byte_width=2, max_amplitude=0.2)
    #play_Audio(audio)
    export_test(audio, to_infinity_curve_test)

def lowpass_FIR_test():
    #s = WAV(african)[10e3:20e3]*LowPassBasic(cutoff=880, width=100)
    c = Line(55,110, 3e3) | Constant(110,2e3)
    c |= Line(110, 220, 3e3) | Constant(220, 2e3)
    c |= Line(220, 440, 3e3) | Constant(440, 2e3)
    c |= Line(440, 880, 3e3) | Constant(880, 2e3)
    s = Sine(frequency=c, duration=20e3)[0:2]
    s[1] *= LowPassBasic(cutoff=330, width=100)
    audio = s.mixdown(sample_rate=44100, byte_width=2, max_amplitude=0.2)
    #play_Audio(audio)
    # reverse h?
    # using parallel track computation (should be 0.05 the time)
    #export_test(audio, lowpass_FIR_test)

def Butterworth_test():
    s = WAV(african)[10e3:20e3]
    s[1] *= Butterworth(cutoff=880)
    audio = s.mixdown(sample_rate=44100, byte_width=2, max_amplitude=0.2)
    play_Audio(audio)
    #export_test(audio, lowpass_FIR_test)


def test_something():
    ...

if __name__ == "__main__":
    Butterworth_test()
    #%%%%%




















