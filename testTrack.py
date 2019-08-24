# -*- coding: utf-8 -*-
"""
Created on Sat Aug 17 23:28:31 2019

@author: Dror
"""

import simpleaudio as sa

from Signal import Sine, Square, Triangle, Sawtooth, GreyNoise, WAV
from transforms import Fade, AmpFreq, Shift, Channels
from audio import Audio
from playback import play_WAV, WAV_to_Audio, play_Audio, export_WAV

def only_signal_harmonics(f=220, seconds=3):
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
    
    t = sum([p[0]*Triangle(frequency=f*p[1], duration=seconds)*\
             AmpFreq(frequency=p[2], size=p[3])*\
             Shift(seconds=3) for p in params])
    
    return t.mixdown()

def simple_test(f=220, seconds=5):
    t = Sine(frequency=230, duration=seconds)*AmpFreq(frequency=1, size=0.2)*Channels((0.7,0.7))
    t += Triangle(frequency=380, duration=seconds)*AmpFreq(frequency=0.4, size=0.3)*Channels((0,1))
    t += Square(frequency=300, duration=seconds)*AmpFreq(frequency=0.7, size=0.2)*Channels((1,0))
    t *= Fade(is_in=True, duration=3)
    #t *= Fade(is_in=False, duration=20)
    t *= Shift(seconds=1)
    return t.mixdown()

def WAV_test(filename=""):
    wav = WAV(WAV_to_Audio(filename), 44100)
    wav *= AmpFreq(frequency=0.06, size=0.3)
    wav *= Fade(is_in=True, duration=10)
    
    wav += 0.03*GreyNoise(duration=20)*AmpFreq(frequency=0.03, size=0.2)
    wav += 0.06*Triangle(frequency=230, duration=30)*Fade(is_in=True, duration=3)*Channels((0.7,0.7))
    
    audio = wav.mixdown(sample_rate=44100)
    
    export_WAV("data/export.wav", audio)
    #play_Audio(ad, is_wait=True)
    
    
def timing_test():
    t = Sine(frequency=230, duration=3)*AmpFreq(frequency=1, size=0.2)*Channels((0.7,0.7))
    t += Square(frequency=250, duration=3)*Shift(seconds=3)
    audio = t.mixdown(sample_rate=11025, byte_width=2)
    play_Audio(audio, is_wait=True)
    
if __name__ == "__main__":
    #timing_test()
    
    x = WAV_test("data/african_sketches_1.wav")
    #
    #%%%%%




