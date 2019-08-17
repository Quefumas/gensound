# -*- coding: utf-8 -*-
"""
Created on Sat Aug 17 21:38:46 2019

@author: Dror
"""

import numpy as np
from utils import stretch

class Track:
    """ represents an audio track onto which one can add signals,
    and which can be exported into audio wav."""
    
    sampleRate = None
    events = None
    channels = None
    audio = None
    
    def __init__(self):
        self.sampleRate = 11025 # default for speed
        self.events = []
        self.channels = 1
        self.duration = 0
    
    def append(self, signal, time):
        self.events.append({"signal":signal, "time":time})
        self.duration = max(self.duration, time + signal.duration)
    
    def stretch(self):
        self.audio = stretch(self.audio, 8*self.byteWidth)
    
    def realise(self, sampleRate=11025, byteWidth=2):
        self.sampleRate = sampleRate
        self.byteWidth = byteWidth
        # create empty audio
        self.audio = np.zeros(self.duration * self.sampleRate) # create np array instead
        
        for event in self.events:
            # perhaps push time into signal class TODO
            signal_audio = event["signal"].realise(self.sampleRate)
            
            # add into mix
            self.audio[event["time"] * sampleRate: \
                       (event["time"]+event["signal"].duration) * sampleRate] \
                       += \
                       signal_audio
        
        self.stretch()
        # TODO int16 is parameter of byteWidth
        self.audio = self.audio.astype(np.int16)
        
        return self.audio
    

















