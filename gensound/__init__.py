# -*- coding: utf-8 -*-

import functools

from .signals import *
from .transforms import *
from .audio import Audio
from .musicTheory import midC


mix = Signal.mix
concat = Signal.concat



import os

kushaura = os.path.join(os.path.dirname(__file__), "data/Kushaura_sketch.wav")
test_wav = kushaura

def transform(f): # decorator for functions masquerading as Transforms
        # TODO better names?
        # TODO leave a sign to distinguish between other functions
        # TODO use wraps()?
        def func_transform(*args):
            def returnable(s):
                return f(s, *args)
            return returnable
        
        return func_transform


# TODO perhaps expose everything inside signals.py and transforms.py,
# leaving amplifiers/filters/effects to be dragged out of their individual files
