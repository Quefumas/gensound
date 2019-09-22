# -*- coding: utf-8 -*-
"""
Created on Wed Sep 11 19:27:49 2019

@author: Dror
"""

import numpy as np
from playback import play_Audio
from Signal import Signal
from transforms import Channels
from musicTheory import midC

class Glis(Signal):
    def __init__(self, frequency=220, duration=3000):
        super().__init__()
        self.frequency = frequency
        self.duration = duration
        
    def integrate(self, freq):
        phase = np.zeros(int(self.sample_rate*self.duration/1000))
        for i in range(1, len(phase)):
            phase[i] = phase[i-1] + 1/self.sample_rate*freq(i/self.sample_rate)
        return phase
        
    def generate(self):
        
        #phase = np.zeros(3*self.sample_rate)
        #phase[0:self.sample_rate] = np.linspace(0, 220, self.sample_rate, False)
        #phase[self.sample_rate:2*self.sample_rate] = 220 + np.linspace(0, 220, self.sample_rate, False) + 55*np.linspace(0,1,self.sample_rate,False)**2
        #phase[2*self.sample_rate:3*self.sample_rate] = phase[2*self.sample_rate-1] + np.linspace(0, 330, self.sample_rate, False)
        
        #return np.sin(2*np.pi*phase)
        
        assert type(self.frequency) == type(lambda x:x)
        phase2 = self.integrate(self.frequency)
        return np.sin(2*np.pi*phase2)
        # TODO perhaps we should define square function dependant on phase, 
        # perhaps sine, triangle etc. all inherit from PitchedSignal
        # which provides capabilities for integrating changing frequency
        
        
def glisTest():
    f = lambda x: 220 if x < 1 else (330 if x > 4 else (220+110*(x-1)/3))
    f2 = lambda x: midC(6)-20 if x < 1 else (midC(1) if x > 4 else (midC(6)-20-(midC(6)-20-midC(1))*(x-1)/3))
    
    signal = Glis(duration=5000, frequency=f)*Channels((1,0))
    signal += Glis(duration=5000, frequency=f2)*Channels((0,1))
    
    audio = signal.mixdown(sample_rate=11025, byte_width=2, max_amplitude=0.01)
    play_Audio(audio, is_wait=True)


if __name__ == "__main__":
    glisTest()






