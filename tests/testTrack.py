# -*- coding: utf-8 -*-
"""
Created on Sat Aug 17 23:28:31 2019

@author: Dror
"""

import numpy as np

from Signal import Signal, Sine, Square, Triangle, Sawtooth, GreyNoise, WAV, Step
from transforms import Fade, AmpFreq, Shift, Channels, Pan, Extend, \
                       Downsample_rough, Average_samples, Amplitude, \
                       Reverse, Repan, Gain, Limiter, Convolution, Slice, \
                       Mono, ADSR
from curve import Curve, Constant, Line, Logistic, SineCurve
from playback import play_WAV, play_Audio, export_test # better than export_WAV for debugging

from musicTheory import midC

african = "../data/african_sketches_1.wav"


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
    
    gap = 0.03
    L = s[10e3:11e3] | gap | s[11e3:12e3] | gap | s[12e3:13e3] | gap | s[13e3:14e3] \
        | gap | s[14e3:15e3] | gap | s[15e3:16e3] | gap | s[16e3:24e3]
    R = s[10e3:18e3] | gap | s[18e3:19e3] | gap | s[19e3:20e3] | gap | s[20e3:21e3] \
        | gap | s[21e3:24e3]
    
    s = L*Repan(0, None) + R*Repan(None, 1)
    
    audio = s.mixdown(sample_rate=44100, byte_width=2, max_amplitude=0.2)
    play_Audio(audio)
    #export_test(audio, concat_scalar_test)
    # this is a funky effect of panning by dephasing...

def reverse_phase_test():
    s = WAV(african)
    
    L = s[10e3:11e3] | -s[11e3:12e3] | s[12e3:13e3] | -s[13e3:14e3] | s[14e3:15e3] \
        | -s[15e3:16e3] | s[16e3:17e3]
    R = s[10e3:17e3]
    
    s = L*Repan(0, None) + R*Repan(None, 1)
    
    audio = s.mixdown(sample_rate=44100, byte_width=2, max_amplitude=0.2)
    #play_Audio(audio)
    export_test(audio, reverse_phase_test)

def channel_slice_test():
    # series of tests
    s = WAV(african)[5e3:15e3]
    
    # t = s[0]
    # t = s[1,1e3:7e3]
    # t = s[1e3:7e3]
    
    #s[1] = 0.132*GreyNoise(duration=10e3)#*Gain(-20)
    
    #s[0,3e3:7e3] = s[1,2e3:6e3]
    #s[0,1e3:6e3] += 0.13*Sine(frequency=midC(8))
    #s[0,1e3:5e3] *= Reverse()
    #s[1] = s[0]*Gain(-6)
    # etc...
    
    t = s[0]*Channels(0,1)
    t[0] = 0.1*Sine()
    audio = t.mixdown(sample_rate=44100, byte_width=2, max_amplitude=0.2)
    play_Audio(audio)
    #export_test(audio, channel_slice_test)

def test_gain_dB():
    s = Signal()
    
    for i in range(10):
        s |= Sine(duration=1e3)*Gain(-6*i)
    
    audio = s.mixdown(sample_rate=44100, byte_width=2, max_amplitude=0.2)
    play_Audio(audio)

def test_filter_noise():
    g = GreyNoise()
    g *= Average_samples(0.04, 0.12, 0.2, 0.12, 0.04)
    #g *= Average_samples(5)
    audio = g.mixdown(sample_rate=11025, byte_width=2, max_amplitude=0.2)
    play_Audio(audio)


def pan_mono_test():
    panLaw = -3
    panMax = 100
    panMin = -100
    width = panMax - panMin
    
    pan_shape = lambda x: np.log((x+panMax+0.1)/(width)) # +0.1 to prevent log(0)
    LdB = lambda x: panLaw*pan_shape(x)/pan_shape(0)
    RdB = lambda x: LdB(-x)
    
    L = lambda t: LdB(width*t/5 + panMin)
    R = lambda t: RdB(width*t/5 + panMin)
    
    # =-===========
    s = Sine(duration=10e3)*Channels(1,0)
    s[2.5e3:7.5e3] *= Pan(L, R)
    s[7.5e3:] *= Repan(1, 0)
    
    audio = s.mixdown(sample_rate=11025, byte_width=2, max_amplitude=0.2)
    play_Audio(audio)
    #export_test(audio, pan_mono_test)

def test_reverse_channels():
    s = WAV(african)[15e3:25e3]
    s[0] += (WAV(african)[15e3:35e3:2]*Gain(-6))[1]
    s[1] += (WAV(african)[15e3:45e3:3]*Gain(-6))[0]
    s = s[1::-1]
    audio = s.mixdown(sample_rate=24000, byte_width=2, max_amplitude=0.2)
    play_Audio(audio)
    #export_test(audio, test_reverse_channels)

def test_to_stereo_syntax():
    s = Sine()[0:2] # automatically casts into stereo
    s[0] += 0.2*Triangle(frequency=360)
    audio = s.mixdown(sample_rate=11025, byte_width=2, max_amplitude=0.2)
    play_Audio(audio)

def test_implicit_add_channel():
    s = Sine() #[0:2]
    #s[0] += 0.4*Triangle(duration=6e3) # exceeding signal bounds in time
    s[2] = 0.2*Triangle() # channels it into mono channel with empty R
    #print(s)
    audio = s.mixdown(sample_rate=11025, byte_width=2, max_amplitude=0.2)
    #play_Audio(audio)
    export_test(audio, test_implicit_add_channel)

def test_to_mono():
    s = WAV(african)[15e3:25e3]
    ### s = sum(s) # raises error - we do not know how many channels there are
    s = s[0] + s[1] # use this
    #s *= Mono() # or this
    audio = s.mixdown(sample_rate=24000, byte_width=2, max_amplitude=0.2)
    play_Audio(audio)

def test_reverse_channels_2():
    s = WAV(african)[15e3:25e3]
    s[0], s[1] = s[1], s[0] # this works
    audio = s.mixdown(sample_rate=24000, byte_width=2, max_amplitude=0.2)
    play_Audio(audio)

def test_amplitude_param():
    s = WAV(african)[15e3:25e3]
    c1 = Constant(1, 3e3) | Line(1, 0.01, duration=7e3)
    c2 = SineCurve(frequency=3, depth=0.3, baseline=0.7, duration=10e3)
    s *= Amplitude(c1, c2)
    audio = s.mixdown(sample_rate=24000, byte_width=2, max_amplitude=0.2)
    play_Audio(audio)
    # export_test(audio, test_amplitude_param)

def test_gain_param():
    s = WAV(african)[15e3:28e3]
    c1 = Line(-80,0,duration=8e3)
    c2 = Line(-40,-6,duration=4e3)
    s *= Gain(c1, c2)
    s[1,4e3:] *= Gain(-6)
    audio = s.mixdown(sample_rate=24000, byte_width=2, max_amplitude=0.2)
    play_Audio(audio)
    # export_test(audio, test_gain_param)

def test_ADSR():
    notes = [-3, -6, 1, 4, 3, -1, 1, 9, 8, 4, 6]*2
    melody = Signal.concat(*[ Square(frequency=midC(notes[i]), duration=0.5e3)*
                             ADSR(attack=0.03e3, decay=0.1e3, sustain=0.8, release=0.02e3, hold=0.1e3)
                            for i in range(len(notes))])
    melody[1] = Signal.concat(*[ Square(frequency=midC(notes[(i+2)%(len(notes))]), duration=0.5e3)*
                             ADSR(attack=0.03e3, decay=0.1e3, sustain=0.8, release=0.02e3, hold=0)
                            for i in range(len(notes))])
    melody *= Average_samples(5)
    audio = melody.mixdown(sample_rate=24000, byte_width=2, max_amplitude=0.2)
    #play_Audio(audio)
    export_test(audio, test_ADSR)

def test_something():
    ...

if __name__ == "__main__":
    #pan_mono_test()
    test_ADSR()
    #%%%%%




















