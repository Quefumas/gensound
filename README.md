# Gensound
Audio processing and generation framework


This is a lightweight library designed for:
* audio manipulation
* audio synthesis
* musical experiments
* electronic composition

Core features:
* Light-weight
* Easy to use (based on NumPy syntax)
* Offline sound generation
* Flexible - it does not take much work to implement new audio or signal effects
* Learner friendly - the inner workings are accessible and easily understood for those of us who are interested in music, sound, and DSP.
* Supports parametrization and multiple channels
* Supports user-defined custom panning schemes to serve any number of channels

## What Can It Do?

## Show Me How It Looks Like
* Mix a Stereo WAV file to mono:
```python
from Signal import WAV

wav = WAV(filename) # load stereo WAV file

wav = wav[0] + wav[1] # mixes L and R channels together

audio = s.mixdown(sample_rate=44100, byte_width=2) # convert to byte samples

play_Audio(audio) # play (alternatively, export)
```

* Reverse L/R channels in stereo WAV file:
```python
wav[0], wav[1] = wav[1], wav[0]
```

* Add a 60Hz sine wave to the left channel of a WAV file, 4 seconds after the beginning:
```python
from Signal import Sine, WAV

wav = WAV(filename) # assumes 'filename' is a stereo WAV file

wav[0,4e3:] += Sine(frequency=60, duration=2e3)*Gain(-9) # mix a sine wav to the L channel, starting at 4000ms

audio = wav.mixdown(sample_rate=44100, byte_width=2)
play_Audio(audio)
```

* Play the R channel of a WAV file in reverse:
```python
from transforms import Reverse

wav[0] *= Reverse()
```

* Haas effect using slice notation - every second the R channel skips a sample, giving the illusion that the sound is coming from the left
```python
srate = 44100
wav[0] = wav[0,:srate] | wav[0,srate+1:2*srate] | wav[0,2*srate+1:] # TODO
```

* Imitate electric guitar amplifier and reverb effect:
```python
from transforms import GuitarAmp_Test, OneImpulseReverb

guitar = WAV(guitar_clean)

guitar *= Gain(20)*GuitarAmp_Test(harshness=10, cutoff=4000)*OneImpulseReverb(mix=1.2, num=2000, curve="steep")

audio = guitar.mixdown(sample_rate=44100, byte_width=2)
export_WAV("guitar_distortion.wav", audio)
```

## Setup
* At the moment there is no automatic installation, simply download the files in the root directory (the child directories are not used). This will definitely change in the future.
* Currently uses the cross-platform, low-dependency [SimpleAudio](https://github.com/hamiltron/py-simple-audio) for audio and WAV file I/O. This may change in the future as well.
* Requires NumPy for a lot of arithmetic. Probably any non-ancient version will do. This will never change.
* A few small features require SciPy as well. I aspire to make SciPy at least optional.

## Proper Explanations

The library is built on two classes:
* Signal - this represents a stream of multi-channeled samples, either raw (e.g. loaded from WAV file) or mathematically computable (e.g. a Sawtooth wave)
* Transforms - this represents a process that can be applied to a Signal (for example, reverb, filtering, gain, reverse, slicing)

With these two classes we can perform many operations, all of which return a new Signal object:
* `Signal + Signal`: mix two signals together
* `Signal | Signal`: concatenate two signals one after the other
* `Signal**4`: repeat the signal 4 times
* `Signal*Transform`: apply `Transform` to `Signal`
* `Signal[0]`: obtain the first channel of Signal
* `Signal[:,:4e3]`: obtain the first 4 seconds of Signal










