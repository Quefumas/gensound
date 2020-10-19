# -*- coding: utf-8 -*-
"""
Created on Tue Sep 29 20:11:46 2020

@author: Dror
"""

from gensound import Sine, Step, Extend, Shift, mix, midC, play_Audio, export_WAV

def chords():
    s = Sine(frequency=midC(-3), duration=5e3)
    s = mix([Sine(f,2e3) for f in ("G", "C5", "Eb5")])
    s |= mix([Sine(f,2e3) for f in ("A", "C5", "E5")])
    s |= mix([Sine(f,2e3) for f in ("Ab", "C5", "F5")])
    s |= mix([Sine(f,0.66e3) for f in ("G#", "C#5", "E5")])
    s |= mix([Sine(f,0.67e3) for f in ("G#-33", "C#5-33", "E5-33")])
    s |= mix([Sine(f,0.67e3) for f in ("G#-66", "C#5-66", "E5-66")])
    s |= mix([Sine(f,2e3) for f in ("G", "C5", "Eb5")])
    a = s.mixdown(44100, 2, 0.3)
    play_Audio(a, is_wait=True)

if __name__ == "__main__":
    chords()