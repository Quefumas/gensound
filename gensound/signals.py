# -*- coding: utf-8 -*-

import copy

import numpy as np

from gensound.utils import isnumber, iscallable, num_samples
from gensound.musicTheory import parse_melody_to_signal, read_freq

from gensound.transforms import Transform, TransformChain, Amplitude, Slice, Combine, BiTransform
from gensound.curve import Curve
from gensound.audio import Audio

#CHANNEL_NAMES = {"L":0, "R":1}


__all__ = ["Signal", "Silence", "Step", "WhiteNoise", "Sine", "Triangle",
           "Square", "Sawtooth", "Raw", "WAV"]

class Signal:
    def __init__(self):
        self.transforms = []
    
    #@abstractmethod ???
    def generate(self, sample_rate):
        """
        this is the part the generates the basic signal building block
        ####should return 2d np.ndarray
        should return 1d np.ndarray, the dims are fixed later...
        not sure if good
        TODO
        new: can also return Audio if there is a need;
        but generally should be np.ndarray
        """
        return np.zeros(shape=(1,0))
    
    def realise(self, sample_rate):
        """ returns Audio instance.
        parses the entire signal tree recursively
        """
        audio = self.generate(sample_rate)
        
        if not isinstance(audio, Audio):
            audio = Audio(sample_rate).from_array(audio)
    
        for transform in self.transforms:
            transform.realise(audio=audio)
            
        return audio
    
    mixdown = realise # TODO consider keeping just 1
    
    def play(self, sample_rate=44100, **kwargs):
        audio = self.realise(sample_rate)
        return audio.play(**kwargs)
    
    def export(self, filename, sample_rate=44100, **kwargs):
        audio = self.realise(sample_rate)
        audio.export(filename, **kwargs)
    
    def to_bytes(self, sample_rate=44100, **kwargs):
        audio = self.realise(sample_rate)
        audio._prepare_buffer(**kwargs)
        return audio.buffer
    
    #####################
    def num_samples(self, sample_rate):
        return num_samples(self.duration, sample_rate)
    
    def sample_times(self, sample_rate):
        stop_time = self.duration/1000 if isinstance(self.duration, float) \
            else self.duration/sample_rate
        return np.linspace(start=0, stop=stop_time, num=self.num_samples(sample_rate), endpoint=False)
    
        
    def copy(self):
        """
        creates an identical signal object.
        """
        # TODO perhaps deepcopy should be overridden to be thinner and faster,
        # since it is performed often
        return copy.deepcopy(self)
    
    @staticmethod
    def concat(*args):
        """
        If receives a single Signal, return it unchanged.
        If receives a list/tuple of Signals, return a Sequence object containing them
        If receives multiple arguments, return a Sequence containing them
        """
        if len(args) == 1:
            if isinstance(args[0], Signal):
                return args[0]
            else: # assumes tuple/list/iterable
                return Sequence(*args[0])
        return Sequence(*args)
    
    @staticmethod
    def mix(args):
        # we really want to use #reduce(, args) instead
        # but the question is what should be the 1st argument?
        return sum(args)
    
    ####### sound operations ########
    
    def _amplitude(self, number):
        assert isnumber(number)
        return self*Amplitude(number)
    
    def _apply(self, transform):
        assert not isinstance(transform, BiTransform), "can't apply BiTransform, use concat."
        
        if transform is None:
            return self
        
        if isnumber(transform):
            return self._amplitude(transform)
        
        if iscallable(transform) and not isinstance(transform, Transform):
            # if transform is a function receiving a signal and returning a signal,
            # masquerading as a Transform. Use @transform decorator for those
            return transform(self)
        
        s = self.copy() # TODO is this needed?
        # it is, so we can reuse the same base signal multiple times
        if isinstance(transform, TransformChain):
            s.transforms.extend(transform.transforms)
        else:
            s.transforms.append(transform)
        return s
    
    def _concat(self, other):
        # TODO why is this before mix?
        # TODO consider enabling for negative other,
        # thus shifting a sequence forward(backward? Chinese) in time
        # TODO possibly better way to implement than using Silence
        if other is None:
            return self
        
        if isnumber(other):
            other = Silence(duration=other)
            
        s = Sequence()
        # use isinstance(self, Sequence) instead? more semantic
        # TODO write this as overloading of Sequence operators instead?
        if not self.transforms and isinstance(self, Sequence):
            s.sequence += self.sequence
        else:
            s.sequence += [self]
        
        if isinstance(other, BiTransform): # if concatting BiTransform
            s.sequence[-1] = s.sequence[-1]._apply(other.L)
            s.sequence += [other.R]
            return s
        
        if isinstance(s.sequence[-1], Transform): # if coming out of BiTransform
            t = s.sequence.pop()
        else:
            t = None
        
        if not other.transforms and isinstance(other, Sequence):
            other.sequence[0] = other.sequence[0]._apply(t)
            s.sequence += other.sequence
        else:
            s.sequence += [other._apply(t)]
        
        return s
    
    def _mix(self, other):
        # mixing with constant number is interpreted as DC
        # TODO use @singledispatchmethod for this?
        if isnumber(other):
            # TODO not all Signals define self.duration!
            # This looks like a case for duration inference
            # luckily this isn't actually a very useful feature
            # (though it may be for Curve?)
            other = other*DC(duration=self.duration)
        
        s = Mix()
        
        if not self.transforms and isinstance(self, Mix):
            s.signals += self.signals
        else:
            s.signals += [self]
        
        if not other.transforms and isinstance(other, Mix):
            s.signals += other.signals
        else:
            s.signals += [other]
        
        return s
    
    def _repeat(self, number):
        # repeats this signal several times in a row
        assert isinstance(number, int)
        return Signal.concat(*[self]*number)
    
    def _print_nice(self):
        if isinstance(self, Sequence):
            res = "[{}]".format(" + ".join([str(signal) for signal in self.sequence]))
        elif isinstance(self, Mix):
            res = "({})".format(" + ".join([str(signal) for signal in self.signals]))
        else:
            res = str(type(self).__name__)
        
        res += "" if not self.transforms else "*({})".format(",".join([str(transform) for transform in self.transforms]))
        return res
    
    ####### overloading operators #######
    
    def __str__(self):
        return self._print_nice()
    
    def __pow__(self, other):
        return self._repeat(other)
    
    def __rmul__(self, other):
        """ multiplication from the left is only legal for numbers, not for transforms"""
        return self._amplitude(other)
    
    def __mul__(self, other):
        """
        signals can be multiplied on the right by both floats and transforms
        """
        return self._apply(other)
    
    def __radd__(self, other):
        if other == 0:
            return self
        
        raise TypeError("Signal can only be added to other signals, or to 0.")
    
    def __add__(self, other):
        """
        create empty signal list.
        for each operand, if it is transformed or a single signal,
        append it to the list.
        otherwise, it is an untransformed list, simply extend the signal list.
        """
        return self._mix(other)
    
    def __sub__(self, other):
        return self._mix(-other)
    
    def __neg__(self):
        return self._amplitude(-1.0)
    
    def __or__(self, other):
        """Overloading concat."""
        return self._concat(other)
    
    def __ror__(self, other):
        if other == 0:
            return self
        
        if isnumber(other):
            return Silence(duration=other)._concat(self)
        
        raise TypeError("Signal can only be concatted to other signals, or to 0.")
    
    #########
    @staticmethod
    def __subscripts(arg):
        """ Accepts first arg from __get/setitem__ and expands it to include
        both channel as well as time dimension.
        
        args[1] is relevant only for __setitem__.
        
        if args[0] = int,
            then it is taken to refer to a track, e.g.:
                signal[1] = Sine()
                # channel 1 is now a sine wave
        
        if args[0] = slice of ints,
            then it is taken to refer to tracks, e.g.:
                signal = signal[1::-1] # switches L/R
        
        if args[0] = slice of floats,
            then it is taken to refer to time span only:
                signal[3e3:4e3] *= Reverse()
                # reverse the content in the 3rd second
        
        if args[0] = tuple,
            then args[0][0] refers to channel,
            and args[0][1] refers to timespan:
                signal[1:3,10e3:15e3] *= Fade()
                # Applies fade in time 10s-15s only on channels 1, 2
        
        in addition: if the channel is an int (not slice),
            transform it into an equivalent slice
        """
        assert isinstance(arg, (tuple, int, slice))
        
        if isinstance(arg, tuple):
            assert len(arg) == 2, "improper amount of subscripts"
            assert isinstance(arg[1], slice), "time may only be described as ranges"
            if isinstance(arg[0], int):
                arg = (slice(arg[0], arg[0]+1), arg[1])
            assert isinstance(arg[0], slice)
            return arg
        if isinstance(arg, int):
            return (slice(arg, arg+1), slice(None))
        if isinstance(arg, slice):
            # TODO beware of illegal values
            # if both are None, interpret as channels
            if isinstance(arg.start, (int, type(None))) and isinstance(arg.stop, (int, type(None))):
                # slice of channels
                return (arg, slice(None))
            if isinstance(arg.start, (float, type(None))) and isinstance(arg.stop, (float, type(None))):
                # slice of time
                return (slice(None), arg)
            
            raise TypeError("Slice can't be interpreted: inconsistent types")
        
        raise TypeError("Argument not acceptable as subscript")
    
    def __getitem__(self, *args):
        # TODO deal with out-of-bound values for channels and time
        # for now we enable out-of-bound channels when starting at 0 and audio is mono
        return self.copy()*Slice(*Signal.__subscripts(args[0]))
    
    def __setitem__(self, *args):
        assert isinstance(args[1], Signal)
        # TODO deal with out-of-bound values for channels and time
        # TODO should copy self first?
        # TODO use self.apply instead?
        self.transforms.append(Combine(*Signal.__subscripts(args[0]), args[1]))
    
    # def __getattr__(self, name):
    #     # so we can do signal.L to access left channel (0)
    #     if name in CHANNEL_NAMES:
    #         return self[CHANNEL_NAMES[name]]
        # problems: we need to define self.L differently when its setattr vs. getagttr
        # and also avoid recursion when using setattr
    #     raise AttributeError
    
    def __iter__(self):
        # can't iterate over channels since they're not known until mixdown
        # (transforms affect them during realise)
        # this is to prevent sum(signal) as a way to mix into mono
        # instead of getting into a loop (didn't go deep into that one)
        # 
        raise TypeError("May not iterate over Signal objects, as channel number is unknown prior to mixdown.")

#### other "high-level" signals ##############################3

class Mix(Signal):
    """
    a list of signals to be mixed together
    (AKA "internal node" of the mix tree)
    """
    def __init__(self, *signals):
        super().__init__()
        self.signals = list(signals)
    
    def generate(self, sample_rate):
        audio = Audio(sample_rate)
        
        for signal in self.signals:
            audio += signal.realise(sample_rate)
        
        return audio

class Sequence(Signal):
    """
    a list of signals to be placed one after the other
    """
    def __init__(self, *sequence):
        super().__init__()
        self.sequence = list(sequence)
    
    def generate(self, sample_rate):
        audio = Audio(sample_rate)
        
        #### Phase Inference: TODO should this be here?
        
        phase = 0 # phase inference
        
        for signal in self.sequence:
            if isinstance(signal, Oscillator) and signal.phase is None:
                signal._phase = phase
                phase = (phase + signal.end_phase)%(2*np.pi) # phase inference
            else:
                phase = 0
            
            audio.concat(signal.realise(sample_rate))
            # TODO assymetric with Mix since we don't overload audio.concat
        
        return audio

#### particular signals #########

class Silence(Signal):
    def __init__(self, duration=5e3):
        super().__init__()
        self.duration = duration
    
    def generate(self, sample_rate):
        return np.zeros(self.num_samples(sample_rate), dtype=np.float64)

class Step(Signal): # Impulse? DC?
    def __init__(self, duration=1):
        super().__init__()
        self.duration = duration
    
    def generate(self, sample_rate):
        return np.ones((self.num_samples(sample_rate),), dtype=np.float64)

DC = Step

## TODO step with frequency

class WhiteNoise(Signal):
    def __init__(self, duration=5e3):
        # TODO add seed argument?
        super().__init__()
        self.duration = duration
    
    def generate(self, sample_rate):
        # TODO this may have non-zero DC!
        return 2*np.random.rand(self.num_samples(sample_rate)) - 1

class PinkNoise(Signal):
    def __init__(self, duration=5e3):
        super().__init__()
        self.duration = duration
    
    def generate(self, sample_rate):
        # Adapted from Larry Trammell (https://www.ridgerat-tech.us/pink/pinkalg.htm)
        av = [ 4.6306e-003,  5.9961e-003,  8.3586e-003 ]
        pv = [ 3.1878e-001,  7.7686e-001,  9.7785e-001  ]
    
        # Initialize the randomized sources state
        randreg = np.zeros_like(av)
      
        for i in range(len(av)):
            randreg[i] = av[i]*2*(np.random.rand() - 0.5)
        
        sig = np.zeros(self.num_samples(sample_rate))
        
        for i in range(len(sig)):
            rv = np.random.rand()
            
            for ii in range(len(av)):
                if rv > pv[ii]:
                    randreg[ii] = av[ii]*2*(np.random.rand() - 0.5)
            sig[i] = sum(randreg)
        
        return sig / np.max(np.abs(sig))

# TODO add other colors of noise

#### simple oscillators


class Oscillator(Signal): # virtual superclass
    wave = lambda phase: 0 # phase -> amplitude; subclass should implement this
    
    def __new__(cls, frequency=220, duration=5e3, phase=None):
        # TODO maybe deal with *args, **kwds for more flexibility
        # Here check if frequency is string also
        
        if isinstance(frequency, str):
            if " " in frequency:
                return Signal.concat([cls(note["frequency"],
                                          int(duration*note["beats"]) if isinstance(duration, int) else float(duration*note["beats"]),
                                          phase)
                                      for note in parse_melody_to_signal(frequency)])
            else:
                frequency = read_freq(frequency)
            #return cls(frequency, duration, phase)
            # TODO frequency should be attached manually to the resulting object
        
        if frequency is None:
            return Silence(duration)
        
        if frequency == "":
            return None
        
        #obj = super(Oscillator, cls).__new__(cls)
        #obj.__init__(frequency, duration, phase)
        #return obj
        #return cls(frequency, duration, phase)
        return super(Oscillator, cls).__new__(cls)
        ...
    
    def __init__(self, frequency=220, duration=5e3, phase=None):
        # TODO consider phase being either degrees (int) or radians (float)
        # phase = None indicates try to infer from end of previous osc, or 0
        super().__init__()
        self.frequency = read_freq(frequency) # TODO this should be dealt with in __new__
        self.duration = duration
        self.phase = phase
        # TODO if frequency is a curve then duration should be derived from it?
        # or ignored?
        
    @property
    def end_phase(self): # for later phase inference
        phase = self.phase or 0
        return (phase + 2*np.pi * self.frequency * self.duration / 1000)%(2*np.pi)
    
    def generate(self, sample_rate):
        # TODO currently the [:-1] after the integral is needed,
        # otherwise it would be one sample too long. perhaps there is more elegant solution,
        # maybe passing an argument telling it to lose the last sample,
        # or better, having CompoundCurve give the extra argument telling its
        # children NOT to lose the last sample
        
        if hasattr(self, "_phase") and self.phase is None: # phase inference
            phase = self._phase
        else:
            phase = self.phase or 0
        
        if isinstance(self.frequency, Curve):
            return type(self).wave(phase + 2*np.pi * self.frequency.integral(sample_rate)[:-1])
        return type(self).wave(phase + 2*np.pi * self.frequency * self.sample_times(sample_rate))
        

class Sine(Oscillator): # oscillator? pitch? phaser?
    wave = np.sin

class Triangle(Oscillator): # TODO start at 0, not 1
    wave = lambda phase: 2*np.abs(((phase-0.5*np.pi) % (2*np.pi) - np.pi))/np.pi - 1
    
class Square(Oscillator):
    wave = lambda phase: ((phase % (2*np.pi) < np.pi)*2 - 1).astype(np.float64)

class Sawtooth(Oscillator):
    wave = lambda phase: ((phase+np.pi) % (2*np.pi))/np.pi-1

# TODO sweepsine, periodic impulse

### raw audio signals

class Raw(Signal):
    cache = {}
    """
    Keep track of when the audio is copied;
    we should probably use a view until we start applying transforms.
    I.e. this object should only keep a view, and on generate it should copy.
    """
    def __init__(self, audio=None):
        super().__init__()
        
        if audio != None:
            if not hasattr(self, "key"):
                self.key = f"Raw_{len(Raw.cache)}"
            
            if self._key() not in Raw.cache:
                Raw.cache[self._key()] = audio
        
    def _key(self): # TODO __key__ ?
        return type(self).__name__ + ":" + str(self.key)
    
    def resample(self, sample_rate=44100, method="quadratic"):
        # TODO maybe copy resampled audio under new key which indicates the sample rate change
        # but to do that we need to decide if we clear the previous version from cache,
        # or what is the best way to let the user decide (e.g. what should be the default behavior?)
        # another approach is to add "new_copy" arg to WAV, ensuring it gets a fresh key
        # and reloads the WAV
        self.audio._resample(sample_rate, method)
        return self # so the user can type WAV("a.wav").resample(44100)*Transform() etc.
        ...
    
    @property
    def audio(self):
        # return Audio object, not ndarray, to override sample raes TODO see if this makes sense overall
        return Raw.cache[self._key()]#.audio
    
    def generate(self, sample_rate):
        #return np.copy(self.audio.audio)
        return self.audio.audio
    """
    TODO
    ####think about this more. here we're copying the audio data,
    #### but not the audio object. should we copy the audio object instead maybe?
    we're passing the direct audio buffer.
    since this eventually goes to audio.from_Array, in which np.copy is called,
    this SHOULD not cause problems when using the same shell for different copies
    of the same original signal.
    also what happens if self.audio already has a sample rate, and the two don't agree?
    """


class WAV(Raw):
    cache = {}
    """
    TODO perhaps make Raw.cache instead
    (but make it easily extensible for new subclasses of Raw)
    either way, WAV/Raw objects should not contain
    the actual audio!
    just a key that will only be used in generate().
    this way the object is an empty skeleton.
    
    Raw.cache can be a dictionary with types as keys,
    values are actual caches with keys defined by each subclass individually
    """
    
    def __init__(self, filename):
        # TODO consider adding "new_copy"/"force_copy"/"unique"/"new" boolean arg
        # would be implemented either by appending random nonce to key,
        # or adding counter for number of copies of base key
        self.key = f"WAV_{filename}"
        
        audio = None
        
        if self._key() not in Raw.cache:
            audio = Audio.from_file(filename)
        
        # TODO copy again? so the cache will be eternally independent?
        super().__init__(audio)
    






















