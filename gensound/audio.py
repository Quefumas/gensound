# -*- coding: utf-8 -*-
"""
TODO
do we need all these functions as static?
some may be instance functions, some may belong in utils.
"""

import warnings
import copy

import numpy as np

from gensound.settings import _supported
from gensound.utils import sec, sample_rates


def warning_msg(message, category, filename, lineno, file=None, line=None):
    return '%s: %s\n' % (category.__name__, message)

warnings.formatwarning = warning_msg



class Audio:
    """Basically a wrapper for a numpy array, representing the signal.
    Shape is (tracks, samples), tracks being >= 1.
    This object is mostly dealt with inside Transform and Signal functions,
    and typically should not be used directly unless you're creating new
    Signals or Transforms.
    Don't override too many operators - this is the nuts and bolts,
    not the pretty facade.
    """
    def __init__(self, sample_rate):
        self.shift = 0
        self.sample_rate = sample_rate
        # TODO get rid of sample_rate argument and have optional audio argument
        # that can be np.ndarray or other array or something
        self.audio = np.zeros((1, 0), dtype=np.float64)
    
    def ensure_2d(self): # TODO should move to utils
        """ makes sure self.audio is 2-dimensional,
        since this is not obvious for mono signals.
        """
        # TODO make sure this is called in a hermetic fashion, everywhere it is needed
        if len(self.audio.shape) == 1:
            self.audio.resize((1, self.audio.shape[0]))
            return False # indicating it wasn't 2d
        return True # the shape was fine all along
        
    
    def from_array(self, array):
        """
        converts np.ndarray to Audio.
        if array is not of type np.float64, converts it implicitly!
        note that this normalizes the values to be within [-1,1]
        """
        if not isinstance(array, np.ndarray):
            array = np.asarray(array, dtype=np.float64)
        
        self.audio = array
        self.ensure_2d()
        
        # TODO should we copy?
        # note that this is called practically everytime we generate() a signal!!!
        self.audio = self.audio.copy(order="C")
        
        return self
    
    def copy(self):
        """
        creates an identical Audio object.
        """
        return copy.deepcopy(self)
    
    ####### getters #######
    
    # always get the info from self.audio itself;
    # we manipulate it directly all the time
    @property
    def num_channels(self):
        assert len(self.audio.shape) == 2
        return self.audio.shape[0]
    
    @property
    def is_mono(self):
        return self.num_channels == 1
    
    @property
    def length(self):
        """ Returns length in samples.
        """
        assert len(self.audio.shape) == 2
        return self.audio.shape[1]
    
    @property
    def duration(self):
        """ Returns duration in ms.
        """
        # TODO this appears to be the only method the uses self.sample_rate
        # consider having it as an argument instead of instance variable
        # reply: Audio always has sample rate, so this should always be available.
        return self.length/self.sample_rate*sec
    
    @property
    def shape(self): # TODO consider doing others like this
        return self.audio.shape
    
    def abs_start(self): return self.shift # in samples only
    def abs_end(self): return self.shift+self.length
    
    ######### Unary manipulations #########
    
    """
    
    first make sure other is appropriate type
    can be scalar (if multiply)
    or np.list, in which case we may need to add channels first
    
    length not restrictive
    
    """
    
    def conform(self, other):
        """
        reshapes self.audio so other.audio may be mixed into it.
        
        ensures other is a 2-d ndarray of similar 1st shape,
        and that self.length >= other.length
        and that self has enough channels
        note that this function has side effects for self.audio!
        
        and unfortunately also for other.
        """
        
        assert isinstance(other, Audio), "Audio.conform can only be used between Audios"
        assert other.is_mono or self.is_mono or other.num_channels == self.num_channels
        
        # conforming channels
        if other.is_mono:
            other.from_mono(self.num_channels)
            # TODO warning: this affects other.
        
        if self.is_mono:
            self.from_mono(other.num_channels)
        
        # conforming lengths TODO better way?
        start = min(self.abs_start(), other.abs_start())
        end = max(self.abs_end(), other.abs_end())
        self.push_forward(self.abs_start() - start)
        self.to_length(end - start)
        
    
    
    ### time manipulations ###
    
    def to_length(self, length):
        """ Ensures self.length is at least length, padding with zeros if needed.
        """
        # TODO this and extend, do we need both?
        if self.length >= length:
            return
        
        self.extend(length - self.length)
    
    def extend(self, how_much):
        """ extends all available channels with zeros """
        self.audio = np.pad(self.audio, ((0,0),(0,how_much)), mode="constant", constant_values=0.0)
    
    def push_forward(self, how_much):
        """ pads the beginning with zeros """
         # TODO sister function which truncates beginning when shift < 0? for use in Combine
        if how_much < 0:
            return
        # pad with nothing before and after the channel dimension
        # pad with how_much before the time dimension, 0 after
        self.audio = np.pad(self.audio, ((0,0),(how_much,0)), mode="constant", constant_values=0.0)
        self.shift -= how_much
    
    def _resample(self, sample_rate, method):
        """ Uses interpolation to change the sample rate of the audio
        while retaining spectral content.
        Don't use this directly; better use Raw().resample instead.
        [TODO does this have to be a supported sample rate?]
        """
        if sample_rate not in sample_rates:
            warnings.warn("Resampling audio to non-standard sample rate. "
                          "This is totally fine if you know what you're doing.")
        
        if self.sample_rate == sample_rate:
            return
        from gensound.utils import get_interpolation
        interpolate = get_interpolation(method)
        factor = self.sample_rate / sample_rate
        self.audio = interpolate(self.audio, np.arange(0, self.length-1, factor)) # TODO should it be self.length - 1? seems to say arange gives half-open range...
        self.sample_rate = sample_rate
    
    ### channel manipulations ###
    
    def to_mono(self):
        """ mixes all channels down to one. does not scale!
        """
        self.audio = np.sum(self.audio, 0)
    
    def from_mono(self, num_channels):
        """ duplicates a mono channel into various channels.
        does not scale! """
        assert self.is_mono, "Can't call Audio.from_mono() for non-mono Audio."
        if num_channels == 1:
            return
        self.audio = self.audio.copy() # TODO is this wasteful?
        self.audio.resize((num_channels, self.length), refcheck=False)
        self.audio[:,:] = self.audio[0,:]
        assert self.ensure_2d()
    
    def to_channels(self, num_channels):
        """ ensures there are at least num_channels
        """
        shape = (num_channels-self.num_channels, self.length)
        self.audio = np.vstack((self.audio, np.zeros(shape, dtype=np.float64)))
    
    ######## binary operations ###########
    
    def mix(self, other):
        assert isinstance(other, Audio)
        
        self.conform(other)
        self.audio[:,other.abs_start()-self.abs_start():other.abs_start()-self.abs_start()+other.length] += other.audio
        return self
    
    def concat(self, other):
        assert isinstance(other, Audio)
        
        other.shift += self.length
        self.mix(other)
    
    
    
    ######## Overloading Operators ###########
    ## TODO consider overloading __setitem__, __getitem__,
    # so that we can do operations on audio instead of audio.audio
    # (or is it being too wordy here?)
    # also, choosing a single channel (not a slice) can be dealt with in the process,
    # delegating this responsibility away from Signal.__subscripts
    
    def __radd__(self, other):
        if other == 0:
            return self
        else:
            return other.__add__(self)
    
    def __add__(self, other): # do we want to overload this?
        return self.mix(other)
    
    def __mul__(self, other):
        print("convolution, should not happen")
        # TODO this should be reexamined and perhaps moved into Convolution or sth
        # also delegate to a non-overloaded function first
        if isinstance(other, np.ndarray):
            assert len(other.shape) == 1, "can multiply Audio by np.ndarray only for one-dimensional arrays"
            if other.shape[0] > self.length:
                other = other[0:self.length]
            self.audio[:,0:other.shape[0]] *= other
            return
            
        assert isinstance(other, Audio)
        # for multiplying by a float, we multiply the signal instead
        # TODO also does not support with Audios with differing params
        self.conform(other)
        self.audio[:,other.abs_start()-self.abs_start():other.abs_start()-self.abs_start()+other.length] *= other[:,:]
        return self
    
    
    
    #### test #####
    # these are overloaded for two reasons:
    # 1. brevity (now transforms can modify audio instead of audio.audio; be careful not to lose references though)
    # 2. (more importantly) convenient syntax to access float indices of the audio!
    # the floats handled below are sample numbers which are interpolated.
    def __getitem__(self, key):
        assert len(key) == 2, "Audio objects must be doubly-subscripted for channel and samples"
        samples_key = key[1]
        
        if isinstance(samples_key, slice) and isinstance(samples_key.start, float):
            raise NotImplementedError("Gensound decided against slicing audio with floats because it thought nobody would use that. Let us know?")
            # slice of floats
            #from gensound.utils import get_interpolation
            #interpolate = get_interpolation('quadratic') # TODO use gensound settings for default
            #return interpolate(self.audio[key[0],:], np.arange(samples_key.start or 0.0,
            #                                                   samples_key.stop or self.length - 0.0,
            #                                                   samples_key.step or 1.0))
        
        if isinstance(samples_key, (list, tuple, np.ndarray)) and isinstance(samples_key[0], float):
            # iterable of floats
            from gensound.utils import get_interpolation
            interpolate = get_interpolation('quadratic') # TODO use gensound settings for default
            return interpolate(self.audio[key[0],:], samples_key)
            
        
        return self.audio.__getitem__(key)
    
    def __setitem__(self, key, value):
        return self.audio.__setitem__(key, value)
    
    
    
    ######## prepare for mixdown ########
    """
    we have these as static since in Audio.mixdown(), we do not wish
    to affect self.audio.
    
    
    TODO think more about this. fit() is probably desirable for playback,
    but Audio.buffer property and everything related to conversion to bytes
    should probably belong strictly in io.py.
    
    mixdown() shouldn't even exist.
    we can keep fit() and call it when doing playback or export, since it makes
    sense to have it around, like extend, resample etc.
    But export should actually be called from Signal, and do the rest on its own.
    """
    
    def fit(self, max_amplitude):
        """
        If max_amplitude = None (default), ensure the signal lies within [-1,1],
          shrinking it if necessary (with a warning).
        
        If max_amplitude is a positive number, in which case ensure the signal lies within
          [-max_amplitude, +max_amplitude].
        
        Finally, if max_amplitude = 0, don't touch anything.
        
        TODO do we need all 3 situations? is this the best interface for them?
        
        'destructive' function, called only when exporting or playing.
        """
        assert max_amplitude is None or 0 <= max_amplitude
        
        if max_amplitude == 0:
            warnings.warn("Setting max_amplitude to 0 may result in distorted audio or clipping.")
            # leave signal peaks unchanged
            return
        
        if max_amplitude is not None and max_amplitude > 1:
            warnings.warn("Supplying a value greater than 1 for max_amplitude will likely lead to distorted audio and clipping.")
        
        max_amp = np.max(np.abs(self.audio))
        
        if max_amplitude is None and max_amp <= 1:
            # fits within default range
            return
        
        # shrink/stretch to either max_amplitude or to 1
        if max_amplitude is None:
            warnings.warn(f"Output audio signal amplitude exceeds 1 (max abs. amplitude {max_amp:0.2f}). "
                          "By default, the signal will be shrunk to fit range of [-1, 1] to prevent clipping. "
                          "To prevent this behaviour, set the max_amplitude argument to zero, which leaves the signal untouched, "
                          "or to any positive number, which will stretch/shrink it to match the given peak amplitude.")
            max_amplitude = 1
        
        self.audio = self.audio * (max_amplitude / max_amp)
        
    
    ####### post-mixdown ########
    
    def _prepare_buffer(self, byte_width, max_amplitude):
        """ Attaches byte width to Audio object, and converts audio information
        to bytes object. This is only done in preparation for output (file or playback).
        """
        from gensound.utils import audio_to_bytes
        
        self.push_forward(self.shift)
        self.fit(max_amplitude)
        
        self.byte_width = byte_width
        self.buffer = audio_to_bytes(self.audio, ["uint8","int16","int24","int32"][byte_width-1])
        
        
    def play(self, byte_width=2, max_amplitude=None, **kwargs):
        from gensound.io import IO
        
        self._prepare_buffer(byte_width, max_amplitude) # TODO max amplitude
        return IO.play(self, **kwargs)
    
    @staticmethod
    def from_file(filename, file_format=None): # 2nd argument to force format regardless of file name
        from gensound.io import IO
        
        ext = file_format or filename.split(".")[-1].lower()
        
        if ext in ("wav", "wave"):
            return IO.WAV_to_Audio(filename)
        
        if ext in ("aiff", "aifc", "aif"):
            return IO.AIFF_to_Audio(filename)
        
        # TODO testing
        return IO.file_to_Audio(filename) # catch-all
    
    def to_WAV(self, filename, byte_width=2, max_amplitude=1):
        warnings.warn("Audio.to_WAV to be deprecated; use Audio.export instead.")
        self.export(filename, byte_width, max_amplitude, file_format="wav")
    
    def export(self, filename, byte_width=2, max_amplitude=None, file_format=None):
        import os
        from gensound.io import IO
        
        filename = os.fspath(filename)
        ext = file_format or filename.split(".")[-1].lower()
        
        self._prepare_buffer(byte_width, max_amplitude)
        
        # TODO disentangle export_WAV arguments so that they will be given
        # seperately (or in a config dict) rather than in an Audio object,
        # since the latter is not supposed to hold a buffer nor byte width
        
        if ext in ("wav", "wave"):
            IO.export_WAV(filename, self)
        elif ext in ("aiff", "aifc", "aif"):
            IO.export_AIFF(filename, self)
        else:
            IO.export_file(filename, self)
    
    
    
    
    ###### visualisations ########
    
    def plot(self):
        assert "matplotlib" in _supported, "matplotlib missing, Audio.plot() not available."
        import gensound.visualise
        gensound.visualise._plot_audio(self)
    
    






























    
    