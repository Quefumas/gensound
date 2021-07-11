# -*- coding: utf-8 -*-
"""
Deprecated
"""

import numpy as np
from gensound.audio import Audio

from gensound.musicTheory import freq_to_pitch

def RMS(audio, start, end):
    return (np.sum(audio.audio[:,start:end]**2) / (audio.num_channels*(end-start)))**0.5


def DFT(audio, N, start=0):
    # TODO only supports mono
    return [(sum([audio.audio[0, start+n]*np.cos(2*np.pi*n*m/N) for n in range(0,N)]),
    -sum([audio.audio[0, start+n]*np.sin(2*np.pi*n*m/N) for n in range(0,N)])) for m in range(0,N)]
    
def DFT_window(audio, N, start=0):
    """ use a window function on the signal to reduce leaking """
    triangle_window = lambda n: 2*n/N if n < (1+N/2) else 2 - 2*n/N
    Hanning_window = lambda n: 0.5 - 0.5*np.cos(2*np.pi*n/N)
    Hamming_window = lambda n: 0.54 - 0.46*np.cos(2*np.pi*n/N)
    
    window = triangle_window
    # TODO test this
    return [(sum([window(n)*audio.audio[0, start+n]*np.cos(2*np.pi*n*m/N) for n in range(0,N)]),
    -sum([window(n)*audio.audio[0, start+n]*np.sin(2*np.pi*n*m/N) for n in range(0,N)])) for m in range(0,N)]

def freq_report(audio, N, sample_rate, start=0):
    FT = DFT(audio, N, start)
    freqs = []
    
    for i, X in enumerate(FT):
        freq = i*sample_rate/N
        pitch = freq_to_pitch(freq)
        
        power = X[0]**2 + X[1]**2
        mag = power**0.5
        
        phase = np.arctan(X[1]/X[0])
        
        freqs.append({
            "frequency" : round(freq, 2),
            "pitch"     : pitch,
            "magnitude" : round(mag, 2),
            "phase"     : round(phase, 2),
            })
    
    return freqs
    

def iDFT(freqs, sample_rate):
    """Freqs is list of [Xreal, Ximag]
    """
    
    N = len(freqs)
    
    xs = []
    
    for n in range(N):
        f = 2*np.pi*n/N
        x = sum([real*np.cos(f*m) + imag*np.sin(f*m) for m, (real, imag) in enumerate(freqs)])
        # TODO make sure that imag*cos and real*sin really do cancel each other
        
        xs.append(x / N)
    
    audio = Audio(sample_rate)
    audio.from_array(xs)
    
    return audio

############
    
def DFT2(samples):
    N = len(samples)
    return [sum([samples[n]*np.e**(-1j*2*np.pi*m*n/N) for n in range(N)]) for m in range(N)]

def iDFT2(freqs):
    N = len(freqs)
    return [sum([freqs[n]*np.e**(1j*2*np.pi*m*n/N) for n in range(N)])/N for m in range(N)]


































