# -*- coding: utf-8 -*-
"""
Created on Tue Sep 29 20:11:46 2020

@author: Dror
"""

from gensound import Sine, Step, Extend, Shift, mix, midC, play_Audio, export_WAV, Reverse, Fade
from gensound.filters import LowPassBasic

def chords():
    fades = Fade(duration=0.01e3)*Fade(is_in=False, duration=0.01e3)
    step = 2e3
    s = mix([Sine(f, step)*fades for f in ("G", "C5", "Eb5")])
    s |= mix([Sine(f, step)*fades for f in ("A", "C5", "E5")])
    s |= mix([Sine(f, step)*fades for f in ("Ab", "C5", "F5")])
    s |= mix([Sine(f, step/3)*fades for f in ("G#", "C#5", "E5")])
    s |= mix([Sine(f, step/3)*fades for f in ("G#-33", "C#5-33", "E5-33")])
    s |= mix([Sine(f, step/3)*fades for f in ("G#-66", "C#5-66", "E5-66")])
    s |= mix([Sine(f, step)*fades for f in ("G", "C5", "Eb5")])
    
    s[1] = s*Reverse()
    
    a = s.play(44100, 2, 0.3)

def output_step():
    s = 0.5*Step(duration=1)*Extend(10)*Shift(1)
    s.export("step_test.wav", 48000, 2, 0.5)

if __name__ == "__main__":
    chords()