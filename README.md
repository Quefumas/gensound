# Gensound
The Python way to Audio processing & synthesis.
* Intuitive
* Flexible
* Lightweight

Do you enjoy experimenting with audio?
Learning about signal processing?
Creating and manipulating sounds?

Gensound is a lightweight library designed for:
* Offline Audio Manipulation & Synthesis
* Musical Experiments
* Electronic Composition

Core features:
* Familiar NumPy syntax is easy to learn and yields clarity, flexibility and conciseness
* Easily extensible - combine new functionalities and effects with zero headache
* Educational - perfect for learning about audio and signals
* Customized panning schemes to enable complex placements of variable number of sound sources
* Parametrization

## Code Examples
* Load a WAV into a `Signal` object from filename:
```python
from gensound import WAV, kushaura

wav = WAV(kushaura) # load sample WAV
```

* Generate audio stream from `Signal` object:
```python
audio = wav.mixdown(sample_rate=44100, byte_width=2)
```

* Playback or file export:
```python
audio.play()
audio.to_WAV("test.wav")
```

* Play file using different sample rate:
```python
WAV(kushaura).mixdown(32000, 2).play() # original sample rate 44.1 kHz
```

* Mix a Stereo signal to mono:
```python
wav = 0.5*wav[0] + 0.5*wav[1] # sums up L and R channels together, halving the amplitudes
```

* Switch L/R channels in stereo WAV file:
```python
wav[0], wav[1] = wav[1], wav[0]
```

* Attenuate R channel by 3dB:
```python
wav[1] *= Gain(-3)
```

* Crop 5 seconds from the beginning:
```python
wav = wav[:,5e3:] # both channels, 5000 ms onwards
```
or even easier:
```python
wav = wav[5e3:] # channels omitted; 5e3 is float, automatically interpreted as ms
```

* Grab the first 1000 samples:
```python
wav = wav[:,:1000] # samples are in ints, so don't omit channel slice
```

* Add a 440Hz sine wave to the L channel, 4 seconds after the beginning:
```python
from gensound import Sine

wav[0,4e3:] += Sine(frequency=440, duration=2e3)*Gain(-9)
wav[0,4e3:] += Sine(frequency="A4", duration=2e3)*Gain(-9) # or like this
```

* Reverse the R channel only:
```python
from gensound import Reverse

wav[1] *= Reverse() # use Reverse transform, or:
wav = wav[1,::-1] # manually reverse the samples
```

* Haas effect - delaying the L channel by several samples makes the sound appear to be coming from the right
```python
wav[0] *= Shift(80) # lisen with headphones! try changing the number of samples
```

* Imitate electric guitar amplifier and reverb effect:
```python
from gensound.amplifiers import GuitarAmp_Test
from gensound.effects import OneImpulseReverb

guitar = WAV("guitar_clean.wav")

guitar *= Gain(20)*GuitarAmp_Test(harshness=10, cutoff=4000)*OneImpulseReverb(mix=1.2, num=2000, curve="steep")
```

* AutoPan both L/R channels with different frequency and depth
```python
from gensound.curve import SineCurve

s = WAV(kushaura)[10e3:30e3] # pick 20 seconds of audio

CurveL = SineCurve(frequency=0.2, depth=50, baseline=-50, duration=20e3)
# L channel will move in a Sine pattern between -100 (Hard L) and 0 (C)

CurveR = SineCurve(frequency=0.12, depth=100, baseline=0, duration=20e3)
# R channel will move in a Sine pattern (different frequency) between -100 and 100
    
t = s[0]*Pan(CurveL) + s[1]*Pan(CurveR)
```

## Setup
* Install NumPy (any non-ancient version)
* Install the cross-platform, low-dependency [SimpleAudio](https://github.com/hamiltron/py-simple-audio) for audio and WAV file I/O (this may change one day)
* Download `gensound` directory
* To test, download and run `testPackage.py` and enjoy some microtonal harmonies

## Proper Explanations

The library is based on two core classes:
* `Signal` - a stream of multi-channeled samples, either raw (e.g. loaded from WAV file) or mathematically computable (e.g. a Sawtooth wave). Behaves very much like a `numpy.ndarray`.
* `Transform` - a process that can be applied to a Signal (for example, reverb, filtering, gain, reverse, slicing)

Signals are envisioned as mathematical objects, and the library relies greatly on overloading of arithmetic operations on them, in conjunction with Transforms. All of the following expressions return a modified Signal object:
* `amplitude*Signal`: change Signal's amplitude by a given factor
* `-Signal`: inverts the signal
* `Signal + Signal`: mix two signals together
* `Signal | Signal`: concatenate two signals one after the other
* `Signal**4`: repeat the signal 4 times
* `Signal*Transform`: apply `Transform` to `Signal`
* `Signal[start_channel:end_channel,start_ms:end_ms]`: `Signal` sliced to a certain range of channels and time (in ms). The first slice expects integers; the second expects floats.
* `Signal[start_channel:end_channel,start_sample:end_sample]`: When the second slice finds integers instead of floats, it is interpreted as a range over samples instead of milliseconds. Note that the duration of this signal changes according to the sample rate.
* `Signal[start_channel:end_channel]`: when a single slice of ints is given, it is taken to mean the channels.
* `Signal[start_ms:end_ms]`: if the slice is made up of floats, it is interpreted as timestamps, i.e.: `Signal[:,start_ms:end_ms]`.

The slice notations may also be used for assignments:
```python
wav[4e3:4.5e3] = Sine(frequency=1e3, duration=0.5e3) # censor beep on seconds 4-4.5
wav[0,6e3:] *= Reverb(...) # add effect to L channel starting from second 6
```

Slice notation may also be used to increase the number of channels implicitly:
```python
wav = WAV("mono_audio.wav") # mono Signal object
wav[1] = -wav[0] # now a stereo Signal with R being a phase inverted version of L
```

> Note the convention that floats represent time as milliseconds, while integers represent number of samples.

The overloading of basic arithmetic operators means that we can generate complex signals in a Pythonic way:
```python
f = 220 # fundamental frequency
sawtooth = (2/np.pi)*sum([((-1)**k/k)*Sine(frequency=k*f, duration=10e3) for k in range(1,11)])
# approximates a sawtooth wave by the first 10 harmonics
```

After creating a complex Signal object, containing various Signals to which various Transforms may be applied, use the `Signal.mixdown()` method to resolve the Signal into a third core type, `Audio`, which holds an actual stream of samples, which can then be output to disk or speakers. Gensound resolves the Signal by recursively resolving each of the Signals contained within, and applying the Transforms to the result sequentially. There is no need to go deeper into `Audio` objects for now; it's only needed when one wishes to add their custom Signals and Transforms.

## More
See the [Reference](REFERENCE.md) for a growing list of useful signals and transforms.
We also plan to upload more example code.
To get a better understanding of the underlying code, the reader is invited to the [Technical Guide](TECHNICAL.md).
If you are interested in contributing, check out [Contribution](CONTRIBUTING.md).


## Topics not yet covered
* How to extend Signal and Transform to implement new effects
* Crossfades and BiTransforms
* Curves and parametrization
* Custom Panning Schemes










