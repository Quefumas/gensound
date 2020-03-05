# -*- coding: utf-8 -*-

import numpy as np
from analyze import DFT2

def visualise_FIRs(*FIRs, is_log=False):
    points = []
    
    for fir in FIRs:
        freqs = DFT2(fir)
        mags = np.array([ f.real**2 + f.imag**2 for f in freqs[0:len(freqs)//2] ])
        mags /= max(mags)
        points.append(mags)
    
    import matplotlib.pyplot as plt
    plt.xticks(ticks=[0, len(freqs)//8, len(freqs)//4, 3*len(freqs)//8, len(freqs)//2],
               labels=["0","fs/8","fs/4","3fs/8" ,"fs/2"])
    plt.ylabel('magnitude')
    if is_log:
        plt.yscale('log')
    
    for mags in points:
        plt.plot(range(len(freqs)//2), mags)
    
    plt.show()


if __name__ == "__main__":
    fill = lambda l: l + [0]*(128-len(l))
    basic_avg_fir = lambda n: fill([1/n]*n)
    graded_fir = lambda n: fill([i-0.5 for i in range(1,n//2+2)] + [n//2-i-0.5 for i in range(n//2)])
    FIR_weighted = fill([0.04, 0.12, 0.2, 0.12, 0.04])
    highpass_maybe = fill([-1,-1,-1,-1,10,-1,-1,-1,-1])
    highpass_try = fill([-1,-1,5,-1,-1])
    strange1 = fill([25,16,9,4,1,4,9,16,25])
    strange2 = fill([1,0,0,0,0,0,0,0,0,0,1])
    strange3 = fill([0.5,-1,2,-1,0.5])
    visualise_FIRs(highpass_try, strange3, is_log=True)