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

def after_test_2():
    # test ** as repeat
    s = Signal.concat(Sine(midC(-7+12), 1e3), Sine(midC(-3), 1e3), Sine(midC(-8+12), 1e3), Sine(midC(-1), 1e3))
    s **= 5
    s += WAV(african)
    
    print(s)
    audio = s.mixdown(sample_rate=44100, byte_width=2, max_amplitude=0.2)
    play_Audio(audio, is_wait=True)

def after_test_3():
    b1 = 1.2e3
    b2 = 1e3
    b3 = 0.8e3
    b4 = 1.4e3
    
    p1 = [-6, -3, -8, -1, 1]
    p2 = [9, 4, 6, 8, 11]
    p3 = [12+1, 12+4, 12+6, 12+8, 12+1, 12+3, 12+11]
    p4 = [-12+2, -12-1, -12+1, -12-3]
    
    s = Signal.concat(*[Sine(midC(p), b1) for p in p1])**5
    s += 0.8*Signal.concat(*[Sine(midC(p), b2) for p in p2])**6*Shift(000)
    s += 0.3*Signal.concat(*[Sine(midC(p), b3) for p in p3])**6
    s += 2*Signal.concat(*[Sine(midC(p), b4) for p in p4])**5
    s *= Average_samples(11)
    
    print(s)
    audio = s.mixdown(sample_rate=44100, byte_width=2, max_amplitude=0.2)
    play_Audio(audio, is_wait=False)
    #export_WAV("data/sine loops 4 voices.wav", audio)

def solfege_test_1():
    num_notes = 20
    duration = 0.5e3
    silence = 0.5e3
    starting_note = 0
    Note = Triangle
    
    notes = [Note(starting_note, duration)*Extend(silence)]
    for i in range(num_notes):
        starting_note += np.random.randint(-4, 5)
        notes.append(Note(midC(starting_note), duration)*Extend(silence))
    
    s = Signal.concat(*notes)
    audio = s.mixdown(sample_rate=22050, byte_width=2, max_amplitude=0.2)
    play_Audio(audio, is_wait=False)

def db_fade_test():
    #signal = Sine(duration=4e3)*Fade(is_in=True, duration=1000)
    signal = WAV(african)*Fade(is_in=True, duration=2e3)
    audio = signal.mixdown(sample_rate=44100, byte_width=2, max_amplitude=0.2)
    play_Audio(audio, is_wait=True)

if __name__ == "__main__":
    #cancellation_test()
    #nonmatching_samplings()
    #convolution_test()
    #after_test_3()
    #solfege_test_1()
    db_fade_test()
    #%%%%%




















