# -*- coding: utf-8 -*-
"""
Created on Sat Aug 10 09:24:24 2019

@author: Dror
"""

import numpy as np
from gensound.utils import isnumber

midA = 440
octave = 2

semitone = np.power(octave, 1/12)
cent = np.power(semitone, 1/100)

logSemitone = lambda k: np.log(k)/np.log(semitone)

midC = lambda s: midA*semitone**(-9+s)

def freq_to_pitch(freq):
    A0 = 27.5 # lowest on piano?
    if freq < A0:
        return "-"
    semitones_above_A0 = logSemitone(freq/A0)
    closest_pitch = int(round(semitones_above_A0))
    #breakpoint()
    divergence = semitones_above_A0 - closest_pitch
    
    octave = (closest_pitch + 9) // 12
    named_pitch = ["A","A#","B","C","C#","D","D#","E","F","F#","G","G#"][closest_pitch % 12]
    
    return named_pitch + str(octave) + (" " + ("+" if divergence > 0 else "") + str(int(round(divergence*100))) if round(divergence,2) != 0 else "")

def str_to_freq(f): # this is a hack, better use regex or something else
    """ 'C##4+35' middle C## plus 35 cents
    'A' A4 (octave implied)
    """
    if f in ("r",""):
        return None
    
    cents = 0
    if "+" in f:
        cents = int(f.split("+")[-1])
        f = f.split("+")[0]
    elif "-" in f:
        cents = - int(f.split("-")[-1])
        f = f.split("-")[0]
    
    semi = {"C":0, "D":2, "E":4, "F":5, "G":7, "A":9, "B":11}[f[0]]
    f = f[1:]
    
    while(len(f) > 0 and f[0] in ("#", "b")):
        semi += 1 if f[0] == "#" else -1
        f = f[1:]
    
    if len(f) > 0:
        semi += 12*(int(f)-4) # octave
    
    return midC(semi+cents/100)
        

# TODO make this accessible and modifiable by user
def read_freq(f):
    if isnumber(f):
        return f
    
    if isinstance(f, str):
        return str_to_freq(f)
    
    return f # important for curves





















