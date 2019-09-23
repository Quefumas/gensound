# -*- coding: utf-8 -*-
"""
Created on Sat Aug 17 23:28:31 2019

@author: Dror
"""

import numpy as np

from Signal import Sine, Square, Triangle, Sawtooth, GreyNoise, WAV, Step
from transforms import Fade, AmpFreq, Shift, Channels, Pan, Extend, \
                       Downsample_rough, Average_samples, Amplitude, \
                       Reverse, Repan, Gain
from playback import play_WAV, play_Audio, export_WAV

from musicTheory import midC

african = "data/african_sketches_1.wav"

def envelope_test():
    env = lambda n: (n/1000) if n < 1000 else (0.5+np.sin(2*np.pi*2*n/1000)/2)
    env = lambda n: (0.5+np.sin(2*np.pi*2*n)/2)
    env = lambda n: (0 if n == 0 else np.sin(n)*(min(n, 1)))
    env = lambda n: np.e**(-3+3*(min(n,3))/3)
    wav = Sine(duration=5000)*Amplitude(env)
    
    audio = wav.mixdown(sample_rate=44100, byte_width=2, max_amplitude=0.03)
    play_Audio(audio, is_wait=True)

def reuse_WAV_test():
    wav = WAV("data/african_sketches_1.wav")
    signal = wav*Reverse() + wav*Shift(duration=150)
    audio = signal.mixdown(sample_rate=44100, byte_width=2, max_amplitude=0.09)
    play_Audio(audio, is_wait=True)

def repan_test():
    signal = WAV("data/african_sketches_1.wav")*Repan((1,0)) #switch L/R
    audio = signal.mixdown(sample_rate=44100, byte_width=2, max_amplitude=None)
    play_Audio(audio, is_wait=True)
    pass

def log_amp_test():
    # tests logarithmic scaling of amplitude factors
    signal = WAV(african)*Repan((0,None)) #switch L/R
    signal += 0.125*WAV("data/african_sketches_1.wav")*Repan((None,1))
    audio = signal.mixdown(sample_rate=44100, byte_width=2, max_amplitude=0.5)
    play_Audio(audio, is_wait=True)
    pass

def gain_test():
    signal = WAV(african)*Repan((0,None))
    signal += WAV(african)*Repan((None,1))*Gain(-9)
    audio = signal.mixdown(sample_rate=44100, byte_width=2, max_amplitude=None)
    play_Audio(audio, is_wait=True)
    #export_WAV("data/gain_test.wav", audio)

if __name__ == "__main__":
    #log_amp_test()
    #gain_test()
    repan_test()
    #%%%%%




