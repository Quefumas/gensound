# -*- coding: utf-8 -*-

"""

Code for plotting stuff. Not a core feature, just a fun option.
Relies on matplotlib.

"""

import numpy as np
import matplotlib.pyplot as plt

def _plot_frequency_response(filter, sample_rate):
    def H(z):
        b,a = filter.coefficients(sample_rate)
        num = sum([z**(len(b) - i - 1)*b[i] for i in range(len(b))])
        denom = sum([z**(len(a) - i - 1)*a[i] for i in range(len(a))])
        return num/denom

    
    # https://stackoverflow.com/a/37841802
    

    w_range = np.linspace(0, np.pi, 1000)
    vals = np.abs(H(np.exp(1j*w_range)))
    #plt.xticks(w_range[::50]*sample_rate/2/np.pi)
    plt.xscale('log')
    plt.ylim(0, max(vals)*1.05)
    plt.plot(w_range*sample_rate/2/np.pi, vals)
    
    #plt.show()



def _plot_audio(audio):
    fig, ax = plt.subplots(audio.num_channels)
    
    if audio.is_mono:
        ax = [ax] # pyplot does not return a list in this case
    
    for i in range(audio.num_channels):
        ax[i].plot(np.linspace(0, (audio.length-1)/audio.sample_rate, audio.length), audio.audio[i,:])
        ax[i].set_xlim(0, (audio.length-1)/audio.sample_rate)
    
    #plt.xticks(w_range[::50]*sample_rate/2/np.pi)
    #plt.yscale('log')
    #plt.ylim(0, max(vals)*1.05)
    
    #plt.plot(self.length / self.sample_rate, self.audio)


