# -*- coding: utf-8 -*-
"""
Created on Thu Sep  5 19:07:59 2019

@author: Dror
"""

from analyze import RMS, DFT
from Signal import Sine, Square, Triangle, Sawtooth, GreyNoise, WAV, Step
from transforms import Fade, AmpFreq, Shift, Channels, Pan
from playback import WAV_to_Audio

def test_RMS():
    sine = Sine().mixdown(sample_rate=11025, byte_width=2)
    square = Square().mixdown(sample_rate=11025, byte_width=2)
    wav = WAV(WAV_to_Audio("data/african_sketches_1.wav"), 44100).mixdown(sample_rate=44100, byte_width=2)
    
    print("Sine RMS: {:.2f}\n\
          Square RMS: {:.2f}\n\
          WAV RMS: {:.2f}".format(RMS(sine, 0, 1000),RMS(square, 0, 1000),RMS(wav, 10000, 11000)))


def test_DFT():
    sines = (Sine()+Sine(frequency=330)).mixdown(sample_rate=11025, byte_width=2)
    Fs = DFT(sines, 100)
    mags = [ (f[0]**2 + f[1]**2)**0.5 for f in Fs ]
    return (Fs, mags)

if __name__ == "__main__":
    #test_RMS()
    Fs, mags = test_DFT()
    # TODO DEBUG
