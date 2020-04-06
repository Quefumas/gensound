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
from filters import Average_samples, LowPassBasic, Butterworth, IIR_basic, IIR_general
from curve import Curve, Constant, Line, Logistic, SineCurve, MultiCurve
from playback import play_WAV, play_Audio, export_test # better than export_WAV for debugging

from musicTheory import midC, semitone

african = "../data/african_sketches_1.wav"

### for testing filters

def SweepTest(stay=0.5e3, step=0.5e3): # start at really low A
    start = 55
    octaves = 4
    c = Constant(start, stay)
    
    for octave in range(octaves):
        c |= Line(start, start*semitone**4, step) | Constant(start*semitone**4, stay)
        start *= semitone**4
        c |= Line(start, start*semitone**3, step) | Constant(start*semitone**3, stay)
        start *= semitone**3
        c |= Line(start, start*semitone**5, step) | Constant(start*semitone**5, stay)
        start *= semitone**5
    
    return Sine(frequency=c, duration=(step+stay)*3*octaves+stay)
#########

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
    #s = WAV(african)[10e3:20e3]
    c = Line(55,110, 3e3) | Constant(110,2e3)
    c |= Line(110, 220, 3e3) | Constant(220, 2e3)
    c |= Line(220, 440, 3e3) | Constant(440, 2e3)
    c |= Line(440, 880, 3e3) | Constant(880, 2e3)
    c |= Line(880, 2*880, 3e3) | Constant(2*880, 2e3)
    s = Sine(frequency=c, duration=20e3)[0:2]
    s[1] *= Butterworth(cutoff=880)
    audio = s.mixdown(sample_rate=44100, byte_width=2, max_amplitude=0.2)
    play_Audio(audio)
    #export_test(audio, Butterworth_test)

def Butterworth_experiment():
    s = WAV(african)[10e3:25e3]
    s1 = s[0]*Butterworth(cutoff=880)
    c = Line(-100, 100, 13e3)
    s2 = s[1]*Pan(c)
    t = s1[0:2] + s2
    audio = t.mixdown(sample_rate=44100, byte_width=2, max_amplitude=0.2)
    play_Audio(audio)
    # export_test(audio, Butterworth_experiment)

def additive_complex_sound_test():
    def s(f, duration):
        return sum([(1/i**1.5)*Sine(frequency = f*i, duration=duration)*ADSR((0.01e3)*(i), 0.8, 0.5+(1/(i+2)), 0.02e3) for i in range(1, 20)])
    
    freqs = [midC(-3), midC(1), midC(-4), midC(4), midC(6), midC(2), midC(-1), midC(11)]*2
    duration = 1e3
    
    t = Signal.concat(*[s(f, duration) for f in freqs])
    
    audio = t.mixdown(sample_rate=44100, byte_width=2, max_amplitude=0.2)
    #play_Audio(audio)
    export_test(audio, additive_complex_sound_test)

def IIR_basic_test():
    s = WAV(african)[10e3:20e3]
    s[5e3:] *= IIR_basic() # y(n) = 0.3*x(n) + 0.7*y(n-1)
    audio = s.mixdown(sample_rate=44100, byte_width=2, max_amplitude=0.2)
    # play_Audio(audio)
    export_test(audio, IIR_basic_test)

def IIR_general_test():
    s = WAV(african)[10e3:20e3]
    s[3e3:] *= IIR_general([0,  -0.5,0,0],
                           [0.25, 0.15,0.07,0.03])
    audio = s.mixdown(sample_rate=44100, byte_width=2, max_amplitude=0.2)
    # play_Audio(audio)
    export_test(audio, IIR_general_test)

def sweep_test():
    s = SweepTest()
    s *= Butterworth(cutoff=440)
    audio = s.mixdown(sample_rate=44100, byte_width=2, max_amplitude=0.2)
    play_Audio(audio)

def test_transform_chain():
    s = WAV(african)[10e3:20e3]
    t = Average_samples(5) * Fade(duration=0.5e3)
    t *= Gain(Line(0,-10,3e3) | Line(-10, 0, 5e3))
    s *= t
    audio = s.mixdown(sample_rate=44100, byte_width=2, max_amplitude=0.2)
    play_Audio(audio)

def test_something():
    ...

if __name__ == "__main__":
    #Butterworth_experiment()
    #additive_complex_sound_test()
    #IIR_general_test()
    #sweep_test()
    test_transform_chain()
    # custom_pan_scheme_test() # come back to this?
    #%%%%%




















