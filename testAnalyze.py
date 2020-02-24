# -*- coding: utf-8 -*-
"""
Created on Thu Sep  5 19:07:59 2019

@author: Dror
"""

from analyze import RMS, DFT, freq_report, iDFT
from audio import Audio
from Signal import Sine, Square, Triangle, Sawtooth, GreyNoise, WAV, Step
from transforms import Fade, AmpFreq, Shift, Channels, Pan
from playback import WAV_to_Audio, play_Audio

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

def test_report():
    sample_rate = 11025
    N = 1000
    
    sines = (Sine()+Sine(frequency=330)).mixdown(sample_rate=sample_rate, byte_width=2)
    freqs = freq_report(sines, N, sample_rate, start=0)
    
    return freqs

def test_iDFT():
    sample_rate = 11025
    N = 100
    sets = 100
    duration = 1000
    
    sines = (Sine(duration=duration)+Sine(frequency=400, duration=duration)).mixdown(sample_rate=sample_rate, byte_width=2)
    
    freqs = [DFT(sines, N, start=i*N) for i in range(sets)]
    
    #freqs = DFT(sines, N)
    
    recycled = [iDFT(fs, sample_rate) for fs in freqs]
    
    output = Audio(sample_rate=sample_rate)
    
    for r in recycled:
        output.append(r)
    
    
    output.mixdown(byte_width=2, max_amplitude=None)
    
    play_Audio(output)
    #breakpoint()
    

if __name__ == "__main__":
    #test_RMS()
    #Fs, mags = test_DFT()
    #rep = test_report()
    test_iDFT()
    pass






































