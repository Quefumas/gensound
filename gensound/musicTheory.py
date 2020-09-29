# -*- coding: utf-8 -*-
"""
Created on Sat Aug 10 09:24:24 2019

@author: Dror
"""

import numpy as np

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






















