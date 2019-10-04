# -*- coding: utf-8 -*-
"""
Created on Thu Sep 12 15:04:25 2019

@author: Dror



This file is to store old test functions, for reference and to document
them later as examples.
"""

import numpy as np

from Signal import Sine, Square, Triangle, Sawtooth, GreyNoise, WAV, Step
from transforms import Fade, AmpFreq, Shift, Channels, Pan, Extend, \
                       Downsample_rough, Average_samples, Amplitude, \
                       Reverse, Repan
from playback import play_WAV, play_Audio, export_WAV

from musicTheory import midC

african = "data/african_sketches_1.wav"

def melody_test():
    step = 500
    notes = (midC(0), midC(-3), midC(-7), midC(4), midC(7), midC(-1), midC(2))
    t = sum([Sine(frequency=f, duration=step+100)*
             Fade(is_in=True, duration=step*5)*
             Fade(is_in=False, duration=step+100)*
             Shift(duration=(1+i)*step)
             for (i,f) in enumerate(notes)])
    audio = t.mixdown(sample_rate=11025, byte_width=2)
    play_Audio(audio)

def only_signal_harmonics(f=220, seconds=10):
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
    
    t = sum([p[0]*Triangle(frequency=f*p[1], duration=seconds*1000)*\
             AmpFreq(frequency=p[2], size=p[3])*\
             Fade(is_in=True, duration=3)*\
             Shift(duration=1*1000) for p in params])
    audio = t.mixdown(sample_rate=11025, byte_width=2)
    play_Audio(audio)

def simple_test(f=220, seconds=5):
    t = Sine(frequency=230, duration=seconds*1000)*AmpFreq(frequency=1, size=0.2)*Channels((0.7,0.7))
    t += Triangle(frequency=380, duration=seconds*1000)*AmpFreq(frequency=0.4, size=0.3)*Channels((0,1))
    t += Square(frequency=300, duration=seconds*1000)*AmpFreq(frequency=0.7, size=0.2)*Channels((1,0))
    t *= Fade(is_in=True, duration=3*1000)
    #t *= Fade(is_in=False, duration=20)
    t *= Shift(duration=1*1000)
    play_Audio(t.mixdown())

def WAV_test(filename=""):
    wav = WAV(filename)
    wav *= AmpFreq(frequency=0.06, size=0.3)
    wav *= Fade(is_in=True, duration=10)
    
    wav += 0.03*GreyNoise(duration=20*1000)*AmpFreq(frequency=0.03, size=0.2)
    wav += 0.06*Triangle(frequency=230, duration=30)*Fade(is_in=True, duration=3*1000)*Channels((0.7,0.7))
    
    audio = wav.mixdown(sample_rate=44100, byte_width=2)
    
    export_WAV("data/export.wav", audio)
    #play_Audio(ad, is_wait=True)
    
    
def timing_test():
    t = Sine(frequency=230, duration=3*1000)*AmpFreq(frequency=1, size=0.2)*Channels((0.7,0.7))
    t += Square(frequency=250, duration=3*1000)*Shift(duration=3*1000)
    audio = t.mixdown(sample_rate=11025, byte_width=2)
    play_Audio(audio, is_wait=True)


def pan_test():
    seconds = 10
    t = Sine(frequency=230, duration=seconds*1000)#*AmpFreq(frequency=1, size=0.2)
    t *= Channels((1,1))
    
    top = seconds*11025
    
    pans = (lambda x: np.log(1+(np.e-1)*(top-x)/top),
            lambda x: np.log(1+(np.e-1)*x/top))
    
    
    t *= Pan(pans)
    
    audio = t.mixdown(sample_rate=11025, byte_width=2)
    play_Audio(audio, is_wait=True)


def step_test():
    times = (1, 3)
    
    t = sum([Step()*Shift(duration=time*1000) for time in times])*Extend(1000)
    #t = Step(1)
    audio = t.mixdown(sample_rate=11025, byte_width=2)
    play_Audio(audio)

def downsample_test(filename):
    wav = WAV(filename)
    wav *= Downsample_rough(factor=5, phase=0)
    audio = wav.mixdown(sample_rate=44100, byte_width=2)
    
    play_Audio(audio, is_wait=True)


def averagesample_test(filename):
    wav = WAV(filename)
    #wav *= Average_samples(weights=(5,4,3,2,1,2,3,4,5))
    wav *= Average_samples(weights=(1,1,1,1,1,1,1,1,1))
    #wav *= Average_samples(weights=(25,16,9,4,1,4,9,16,25))
    #wav *= Average_samples(weights=(1,0,0,0,0,0,0,0,1))
    #wav *= Average_samples(weights=(1,-1,1,-1,1,-1,1,-1,1))
    #wav *= Average_samples(weights=(-1,-1,-1,-1,10,-1,-1,-1,-1)) # high pass!
    audio = wav.mixdown(sample_rate=44100, byte_width=2)
    
    play_Audio(audio, is_wait=True)

def dummy_reverb_test():
    filename = "data/african_sketches_1.wav"
    
    #amp = lambda x: 
    #wav = WAV(filename) + WAV(filename)*Amplitude(amp)*Shift(duration=500)
    #wav = WAV(filename)*AmpFreq(frequency=0.12, size=0.25)
    #wav += WAV(filename)*AmpFreq(frequency=0.12, size=0.25, phase=np.pi)*Shift(duration=500)*Average_samples(weights=(1,1,1,1,1,1,1,1,1))
    
    wav = sum([(1-8/10)*WAV(filename)*Shift(duration=100*x)*Average_samples(weights=2*x+1) for x in range(5)])
    wav += 0.6*WAV(filename)*Downsample_rough(factor=5)*Average_samples(weights=5)
    
    audio = wav.mixdown(sample_rate=44100, byte_width=2)
    play_Audio(audio, is_wait=True)
    #export_WAV(filename="data/african_plus_reverb_with_added_lowpass_downsample.wav", audio=audio)

def repan_reverb_test():
    filename = "data/african_sketches_1.wav"
    
    wav = sum([(1-8/10)*WAV(filename)*Shift(duration=100*x)*Average_samples(weights=2*x+1)*Pan((1,0.3)[::(1 if x%2==0 else -1)]) for x in range(5)])
    wav += 0.6*WAV(filename)*Pan((0,None))*Downsample_rough(factor=5)*Average_samples(weights=5)
    wav += 0.6*WAV(filename)*Pan((None,1))
    
    audio = wav.mixdown(sample_rate=44100, byte_width=2)
    play_Audio(audio, is_wait=True)

def reverse_test():
    wav = WAV("data/african_sketches_1.wav")*Reverse()*Downsample_rough(factor=5)*Average_samples(weights=5)
    wav += WAV("data/african_sketches_1.wav")*Shift(duration=150)*Average_samples(weights=(1,1,1,1,1,1,1,1,1))
    
    audio = wav.mixdown(sample_rate=44100, byte_width=2, max_amplitude=0.09)
    play_Audio(audio, is_wait=True)
    


def t1():
    t = Triangle(frequency=midC(-1.5), duration=5000)*Average_samples(21)*AmpFreq(frequency=0.8, size=0.3)
    
    env = lambda n: (n/1000) if n < 1000 else (0.5+np.sin(2*np.pi*2*n/1000)/2)
    env = lambda n: (0.5+np.sin(2*np.pi*2*n)/2)
    env = lambda n: (0 if n == 0 else np.sin(n)*(min(n, 1)))
    env = lambda n: np.e**(-0.3+0.3*(min(n,0.3))/0.3)
    t += 0.01*Sawtooth(frequency=midC(-1.5), duration=5000)*Amplitude(env)
    
    audio = t.mixdown(sample_rate=44100, byte_width=2, max_amplitude=0.01)
    play_Audio(audio)
    

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

def limit_test():
    signal = WAV(african)
    signal *= Limiter(max_amplitude=0.1)
    #signal *= Limiter(max_ratio=0.9)
    audio = signal.mixdown(sample_rate=44100, byte_width=2, max_amplitude=0.9)
    play_Audio(audio, is_wait=True)


if __name__ == "__main__":
    #repan_reverb_test()
    dummy_reverb_test()
    
    
    
    
    
    
    