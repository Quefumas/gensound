# -*- coding: utf-8 -*-
"""
Created on Sat Aug 10 09:11:41 2019

@author: Dror
"""

import numpy as np
import simpleaudio as sa

from musicTheory import semitone
from params import sampleRate
from utils import stretch, sin, amp_freq, fadeIn

freq1 = 440
freq2 = freq1 * semitone**6
freq3 = freq2 * semitone**5
freq2 = freq1*4/3
freq3 = freq2*6/5

seconds = 10  # Note duration of 3 seconds

#%%%%%%

#note = sin(freq1, 10) + 0.5*sin(freq2, 10) + 0.5*sin(freq3, 10)
#note = amp_freq(note, 2, 10, 0.2)

note = amp_freq(sin(freq1, seconds), 2, seconds, 0.2)
note += 0.5*amp_freq(sin(freq2, seconds), 3, seconds, 0.4)
note += 0.5*amp_freq(sin(freq3, seconds), 2.3, seconds, 0.3)


#%%%%%%%%

def harmonics(f=220):
    seconds = 10
    
    # amplitude, freq*i, amp_freq, amp_size
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
    
    note = params[0][0] * amp_freq(sin(f*params[0][1], seconds), params[0][2], seconds, params[0][3])
    
    for p in params[1:]:
        note += p[0] * amp_freq(sin(f*p[1], seconds), p[2], seconds, p[3])
    
    return note

#%%%%%%%%

note = harmonics()

fadeIn(note, 3)

# Ensure that highest value is in 16-bit range
audio = stretch(note, 16)
audio = audio.astype(np.int16) # Convert to 16-bit data

play_obj = sa.play_buffer(audio, 1, 2, sampleRate)

#c = input("Type something to quit.")
#play_obj.stop()
play_obj.wait_done()


