# -*- coding: utf-8 -*-

import numpy as np
from analyze import DFT2
from curve import Curve, Line, Logistic, SineCurve, Constant
from filters import LowPassBasic

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
        plt.plot(range(len(mags)), mags)
    
    plt.show()

def visualise_windows(*windows, is_log=False):
    windows = [w[0:len(w)] for w in windows]
    
    import matplotlib.pyplot as plt
    if is_log:
        plt.yscale('log')
    
    for w in windows:
        plt.plot(range(len(w)), w)
    
    plt.show()


def visualise_curve(curve, integral=False):
    import matplotlib.pyplot as plt
    sample_rate = 1000
    x = np.linspace(0, curve.duration/1000, num=curve.num_samples(sample_rate))
    y = curve.flatten(sample_rate) if not integral else curve.integral(sample_rate)[:-1]
    plt.plot(x, y)
    plt.show()

def test_visualise_windows():
    fill = lambda l: l + [0]*(128-len(l))
    basic_avg_fir = lambda n: fill([1/n]*n)
    graded_fir = lambda n: fill([i-0.5 for i in range(1,n//2+2)] + [n//2-i-0.5 for i in range(n//2)])
    FIR_weighted = fill([0.04, 0.12, 0.2, 0.12, 0.04])
    highpass_maybe = fill([-1,-1,-1,-1,10,-1,-1,-1,-1])
    highpass_try = fill([-1,-1,5,-1,-1])
    strange1 = fill([25,16,9,4,1,4,9,16,25])
    strange2 = fill([1,0,0,0,0,0,0,0,0,0,1])
    strange3 = fill([0.5,-1,2,-1,0.5])
    blackman = [ 0.42 - 0.5*np.cos(2*np.pi*k/127) + 0.08*np.cos(4*np.pi*k/127) for k in range(128)]
    #blackman = [blackman[k]*(1/128)*np.sin(np.pi*k*12/128)/np.sin(np.pi*k/128)  for k in range(len(blackman))]
    #visualise_FIRs(graded_fir(5), blackman, is_log=False)
    
    lowpass_basic = LowPassBasic(440, 201).coefficients(44100)#[40:60]
    
    #visualise_windows(lowpass_basic)
    visualise_FIRs(lowpass_basic, is_log=True)
    #visualise_FIRs(basic_avg_fir(11), is_log=True)

def test_visualise_curve():
    c = Logistic(220,440, 6e3)
    c = SineCurve(3, 10, 50, 10e3)
    c = Line(1,5,5e3) | Constant(5, 5e3)
    visualise_curve(c, True)

if __name__ == "__main__":
    #test_visualise_curve()
    test_visualise_windows()

















