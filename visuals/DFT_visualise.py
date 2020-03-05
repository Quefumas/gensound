# -*- coding: utf-8 -*-

import numpy as np
from analyze import DFT2

def visualise_FIRs(*FIRs):
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
    plt.yscale('log')
    
    for mags in points:
        plt.plot(range(len(freqs)//2), mags)
    
    plt.show()


if __name__ == "__main__":
    fill_64 = lambda l: l + [0]*(64-len(l))
    basic_avg_fir = lambda n: fill_64([1/n]*n)
    graded_fir = lambda n: fill_64([i-0.5 for i in range(1,n//2+2)] + [n//2-i-0.5 for i in range(n//2)])
    FIR_weighted = [0.04, 0.12, 0.2, 0.12, 0.04] + [0]*59
    highpass_maybe = [-1,-1,-1,-1,10,-1,-1,-1,-1] + [0]*55
    highpass_try = [-1,-1,5,-1,-1] + [0]*59
    strange1 = [25,16,9,4,1,4,9,16,25] + [0]*55
    strange2 = [1,0,0,0,0,0,0,0,0,0,1] + [0]*53
    strange3 = [0.5,-1,2,-1,0.5] + [0]*59
    visualise_FIRs(graded_fir(5), graded_fir(11))