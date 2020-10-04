# -*- coding: utf-8 -*-
"""
Created on Thu Sep  5 19:07:59 2019

@author: Dror
"""

import numpy as np

from analyze import RMS, DFT, freq_report, iDFT, DFT2, iDFT2
from audio import Audio
from Signal import Sine, Square, Triangle, Sawtooth, WhiteNoise, WAV, Step
from transforms import Fade, AmpFreq, Shift, Pan
from playback import WAV_to_Audio, play_Audio, export_WAV


african = "data/african_sketches_1.wav"

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
    
def test_DFT2_and_back():
    sample_rate = 11025
    N = 1000
    sets = 10
    duration = 2500
    
    #sines = (Sine(duration=duration)+Sine(frequency=400, duration=duration)).mixdown(sample_rate=sample_rate, byte_width=2)
    #export_WAV("output/analyze/back1.wav", sines)
    sines = WAV(african)[13e3:15.5e3].mixdown(sample_rate=sample_rate, byte_width=2)
    
    for i in range(sets):
        strip = sines.audio[0,i*N:(i+1)*N]
        freqs = DFT2(strip)
        freqs[50:] *= 0 #np.zeros((len(freqs)-50))
        #breakpoint()
        strip2 = iDFT2(freqs)
        sines.audio[0, i*N:(i+1)*N] = np.real(strip2)
    #breakpoint()
    sines.mixdown(byte_width=2, max_amplitude=0.9)
    export_WAV("output/analyze/back2.wav", sines)
    
    

if __name__ == "__main__":
    #test_RMS()
    #Fs, mags = test_DFT()
    #rep = test_report()
    #test_iDFT()
    test_DFT2_and_back()
    pass






































