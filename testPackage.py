# -*- coding: utf-8 -*-
"""
Created on Tue Sep 29 20:11:46 2020

@author: Dror
"""

from gensound import Sine, mix, midC, play_Audio
#from gensound.filters import IIR_OnePole

s = Sine(frequency=midC(-3), duration=5e3)
s = mix([Sine(f,2e3) for f in (midC(12-5), midC(12), midC(12+3))])
s |= mix([Sine(f,2e3) for f in (midC(12-3), midC(12), midC(12+4))])
s |= mix([Sine(f,2e3) for f in (midC(12-4), midC(12), midC(12+5))])
s |= mix([Sine(f,2e3) for f in (midC(12-4), midC(13), midC(12+4))])
a = s.mixdown(44100, 2, 0.3)
play_Audio(a, is_wait=True)