# -*- coding: utf-8 -*-

from .signals import *
from .transforms import *
from .audio import Audio
from .playback import play_Audio, export_WAV
from .musicTheory import midC


mix = Signal.mix
concat = Signal.concat



import os

kushaura = os.path.join(os.path.dirname(__file__), "data/Kushaura_sketch.wav")




# TODO perhaps expose everything inside signals.py and transforms.py,
# leaving amplifiers/filters/effects to be dragged out of their individual files
