# -*- coding: utf-8 -*-
"""
Created on Sat Aug 17 21:38:46 2019

@author: Dror
"""

import numpy as np
from utils import stretch
from Signal import Signal

# TODO perhaps should be inhertied from signal
class Track(Signal):
    """ represents an audio track onto which one can add signals,
    and which can be exported into audio wav."""
    
    def __init__(self):
        self.sample_rate = 11025 # default for speed
        self.events = []
        self.channels = 1 # handle stereo
        self.duration = 0
    
    # def __iadd__(self, other)???
    def append(self, signal:Signal, time):
        self.events.append({"signal":signal, "time":time})
        self.duration = max(self.duration, time + signal.duration)
    
    def stretch(self):
        self.audio = stretch(self.audio, 8*self.byte_width)
    
    def realise(self, sample_rate=11025, byte_width=2):
        self.sample_rate = sample_rate
        self.byte_width = byte_width
        # create empty audio
        self.audio = np.zeros(self.duration * self.sample_rate) # create np array instead
        
        for event in self.events:
            # perhaps push time into signal class TODO
            signal_audio = event["signal"].realise(self.sample_rate)
            #breakpoint()
            # add into mix
            self.audio[event["time"] * sample_rate: \
                       (event["time"]+event["signal"].duration) * sample_rate] \
                       += \
                       signal_audio
        
        self.stretch()
        # TODO int16 is parameter of byteWidth
        self.audio = self.audio.astype(np.int16)
        
        return self.audio
    

















