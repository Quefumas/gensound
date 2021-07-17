# -*- coding: utf-8 -*-
"""
This file contains the entire interface of the library with the OS.
This includes reading and writing files, and real-time playback.

All of these functionalities should be enclosed in this file,
so as to facilitate cross-platform functionality in the future.

This supports the following basic functionalities:
    * playback from Audio instance
    * Audio instance to file (whatever format possible)
    * file to Audio instance

There is a class for each supported I/O library, which provides these functions
for that library in particular. When this file is loaded, the desired libraries
are determined from settings.py (TODO).


Note: The names defined below should only be imported in audio.py.
The Audio class is the final intermediary between Gensound and the actual IO.


"""

import inspect
import time
import random
import string
import datetime
import platform

import numpy as np

from gensound.settings import _supported, _supported_bin



# resulting filename when internally converting to WAV
def converted_file_naming_scheme(filename): return ".".join(filename.split(".")[:-1]) + ".wav"


_temporary_folder = "gensound_temp"
_temp_files = []


_os = platform.system()


def temp_file_naming_scheme():
    # ugly filenames for temp file to prevent accidental overwriting
    nonce = ''.join(random.choice(string.ascii_lowercase) for i in range(8))
    timestamp = datetime.datetime.now().strftime("%Y_%m_%d__%H_%M_%S")
    return f"{_temporary_folder}/gensound_temp_{timestamp}_{nonce}.wav"

def file_exists(filename):
    import pathlib
    return pathlib.Path(filename).is_file()

def export_to_temp_wav(audio):
    import os
    filename = temp_file_naming_scheme()
    
    os.makedirs(_temporary_folder, exist_ok=True)
    
    _IO_wave.export_WAV(filename, audio)
    _temp_files.append(filename)
    print(f"Temp file created at: {os.getcwd()}\{filename}")
    return filename



# we start with the support for the various libraries,
# put the exported functionality down below

class _IO_wave:
    name = "wave"
    is_supported = True # python built-in
    
    @staticmethod
    def export_WAV(filename, audio):
        import wave
        
        file = wave.open(filename, "wb")
        file.setnchannels(audio.num_channels)
        file.setsampwidth(audio.byte_width)
        file.setframerate(audio.sample_rate)
        file.setnframes(audio.length)
    
        file.writeframes(audio.buffer)
    
    @staticmethod
    def WAV_to_Audio(filename): # filename can also be file-like object (used in _IO_ffmpeg)
        import wave
        
        with wave.open(filename, "rb") as file:
            buffer = np.frombuffer(file.readframes(file.getnframes()),
                                   [np.uint8,np.int16,None,np.int32][file.getsampwidth()-1])
            buffer = buffer.astype(np.float64)
            
            buffer = np.reshape(buffer,
                                newshape=(file.getnchannels(),
                                          int(len(buffer)/file.getnchannels()))[::-1]).T.copy(order='C')
            buffer /= 2**(8*file.getsampwidth()-1)
            
            from gensound.audio import Audio
            audio = Audio(file.getframerate())
            audio.from_array(buffer)
        
        return audio

class _IO_aifc:
    name = "aifc"
    is_supported = True # python built-in
    
    @staticmethod
    def export_AIFF(filename, audio):
        import aifc
        
        with aifc.open(filename, "wb") as file:
            file.setnchannels(audio.num_channels)
            file.setsampwidth(audio.byte_width)
            file.setframerate(audio.sample_rate)
            file.setnframes(audio.length)
            
            file.writeframes(audio.buffer.byteswap()) # AIFF byteswap
    
    @staticmethod
    def AIFF_to_Audio(filename):
        # when making changes, consider WAV_to_Audio as well
        import aifc
        
        with aifc.open(filename, "rb") as file:
            buffer = np.frombuffer(file.readframes(file.getnframes()),
                                   [np.uint8,np.int16,None,np.int32][file.getsampwidth()-1])
            buffer = buffer.byteswap().astype(np.float64) # byte swap for AIFF only, not WAV
            
            buffer = np.reshape(buffer,
                                newshape=(file.getnchannels(),
                                          int(len(buffer)/file.getnchannels()))[::-1]).T.copy(order='C')
            buffer /= 2**(8*file.getsampwidth()-1)
            
            from gensound.audio import Audio
            audio = Audio(file.getframerate())
            audio.from_array(buffer)
            
        return audio
    

class _IO_SA:
    name = "simpleaudio"
    is_supported = "simpleaudio" in _supported
    
    @staticmethod
    def playback(audio, wait=True): # plays Audio instance
        import simpleaudio as sa
        #audio.buffer = audio.buffer.copy(order='C')
        play_obj = sa.play_buffer(audio.buffer,
                                  num_channels=audio.num_channels,
                                  bytes_per_sample=audio.byte_width, # TODO should Audio store this?
                                  sample_rate=audio.sample_rate)
        
        if not wait or audio.audio.shape[1] > 3*10**5: # TODO this number is too arbitrary (also doesn't reflect actual duration due to sample rate)
            input("Type something to quit.")
            play_obj.stop()
        else:
            play_obj.wait_done()


class _IO_ffmpeg:
    name = "ffmpeg"
    is_supported = "ffmpeg" in _supported_bin
    
    @staticmethod
    def convert(filename, new_name):
        # currently not available for user, but may be useful in the future
        import subprocess
        
        args = ['ffmpeg', '-i', filename, new_name]
        
        process = subprocess.Popen(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) 
        out, err = process.communicate(None)
        #retcode = process.poll()
    
    @staticmethod
    def file_to_Audio(filename, *args, **kwargs):
        import subprocess, io
        
        args = ['ffmpeg', '-i', filename, '-f', 'wav', 'pipe:']
        
        process = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
        
        return _IO_wave.WAV_to_Audio(io.BytesIO(process.stdout.read()))
    
    @staticmethod
    def export_file(filename, audio):
        # TODO get format from filename or from caller?
        import subprocess
        
        fmt = ["u8", "s16le", "s24le", "s32le"][audio.byte_width-1]
        
        
        args = ['ffmpeg', '-f', fmt, '-ac', str(audio.num_channels), '-i', 'pipe:', filename, '-y']
        
        process = subprocess.Popen(args, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        process.stdin.write(audio.buffer)
        process.stdin.close()
        
        #out = process.stdout.read() # use stdout=subprocess.PIPE above for this
        #err = process.stderr.read()
        
        #print(out)
        #print(err)
        
        
class _IO_ffmpeg_python:
    name = "ffmpeg-python"
    is_supported = "ffmpeg-python" in _supported
    
    @staticmethod
    def convert(filename, new_name):
        import ffmpeg
        # currently not available for user, but may be useful in the future
        ffmpeg.input(filename).output(new_name).run(quiet=True)
    
    @staticmethod
    def file_to_Audio(filename):
        import ffmpeg, io
        
        process = ffmpeg.input(filename).output("pipe:", format="wav").run_async(pipe_stdout=True, quiet=True)
        
        return _IO_wave.WAV_to_Audio(io.BytesIO(process.stdout.read()))
    
    @staticmethod
    def export_file(filename, audio):
        # TODO get format from filename or from caller?
        import ffmpeg
        
        # combine this with similar code in ffmpeg class
        fmt = ["u8", "s16le", "s24le", "s32le"][audio.byte_width-1]
        
        process = (ffmpeg.input("pipe:", format=fmt, ac=audio.num_channels)
                    .output(filename)
                    .overwrite_output()
                    .run_async(pipe_stdin=True, quiet=True))
        process.stdin.write(audio.buffer)
        process.stdin.close()
        process.wait()


class _IO_playsound: # https://github.com/TaylorSMarks/playsound
    name = "playsound"
    is_supported = "playsound" in _supported
    
    @staticmethod
    def playback(audio, **kwargs): # TODO also has "block" arg which may be nice
        
        filename = export_to_temp_wav(audio)
        
        # TODO clear up temp file
        from playsound import playsound
        playsound(filename)
        


class _IO_pygame:
    name = "pygame"
    is_supported = "pygame" in _supported
    
    @staticmethod
    def playback(audio, **kwargs):
        import pygame as pg
        
        # TODO bytewidth can also be over ooptions, also 24 bits not entirely supported yet
        pg.mixer.quit()
        pg.mixer.init(frequency=audio.sample_rate,
                      channels=audio.num_channels,
                      size=[8,-16,-24,-32][audio.byte_width-1],
                      allowedchanges=0 #pg.AUDIO_ALLOW_FREQUENCY_CHANGE
                      )
        # print(pg.mixer.get_init())
        snd = pg.mixer.Sound(buffer=audio.buffer)
        snd.play(**kwargs)
        
        return snd # currently goes nowhere


class _IO_winsound: # fallback for windows
    name = "winsound"
    is_supported = _os == "Windows" # this doesn't appear in _supported for some reason
    
    @staticmethod
    def playback(audio, **kwargs):
        try:
            import winsound
            print("Note: falling back to winsound module via export to temporary file. "
              "It is recommended to install one of the supported I/O libraries for more flexible playback, "
              "for example simpleaudio, pygame or playsound (see docs). ")
            
            filename = export_to_temp_wav(audio)
            
            # TODO it seems it's possible to directly feed bytes to winsound, without temporary file
            # need to consider how to feed num. channels etc.
            winsound.PlaySound(filename, winsound.SND_FILENAME | winsound.SND_ASYNC)
        except:
            _IO_os.playback(audio, **kwargs) # fallback on OS


# fallback class, exporting to wave and opening with OS default player
class _IO_os: # TODO test on all platforms
    name = "os"
    is_supported = True
    
    @staticmethod
    def playback(audio, **kwargs):
        print("Note: falling back to playback by exporting to temporary file then using system default player. "
              "It is recommended to install one of the supported I/O libraries for more flexible playback, "
              "for example simpleaudio, pygame or playsound (see docs for more). ")
        
        filename = export_to_temp_wav(audio)
        
        if _os == 'Windows':
            cmd = f'start "" "{filename}"'
        elif _os == 'Darwin': # Mac OS
            cmd = f'open "{filename}"'
        else: # Linux
            cmd = f'xdg-open "{filename}"'
        
        import os
        os.system(cmd)
        

#### EXPORTED NAMES ##########
'''
Here are the exported functionalities.
TODO add logic to figure out supported libraries (also let user customize),
and direct traffic to the correct classes.
also figure out how to navigate different formats
'''

_io_alternatives = [_IO_wave, _IO_aifc, _IO_SA, _IO_ffmpeg, _IO_playsound, _IO_ffmpeg_python, _IO_pygame, _IO_winsound, _IO_os] 
_io_alternatives = {c.name:c for c in _io_alternatives} # as a dictionary for user interaction later

play_options = (_IO_pygame, _IO_SA, _IO_playsound, _IO_winsound, _IO_os)
load_options = {"wav": (_IO_wave,),
                "aiff": (_IO_aifc,),
                "*": (_IO_ffmpeg_python, _IO_ffmpeg)}
export_options = {"wav": (_IO_wave,),
                  "aiff": (_IO_aifc,),
                  "*": (_IO_ffmpeg_python, _IO_ffmpeg)}


# this will be the eventual interface from Audio,
# and will take care of the logic to decide which libraries to use
def _choose_first_supported(options):
    for o in options:
        if o.is_supported:
            return o
    
    return None

class IO:
    play_cls = _choose_first_supported(play_options)
    load_cls = {fmt: _choose_first_supported(load_options[fmt]) for fmt in load_options}
    export_cls = {fmt: _choose_first_supported(export_options[fmt]) for fmt in export_options}
    
    @staticmethod
    def status(show_options=False): # print_status? since we may want to receive it programmatically as well
        # prints to user status of default and supported I/O capabilities
        print("\n --- Gensound I/O support status ---")
        print(f" playback: {IO.play_cls.name if IO.play_cls else '-'}{'' if not show_options else ' (' + ', '.join([cls.name for cls in play_options if cls.is_supported and cls != IO.play_cls]) + ')'}")
        
        print("\n load:")
        
        for fmt in IO.load_cls:
            print(f"    {fmt}: {IO.load_cls[fmt].name if IO.load_cls[fmt] else '-'}{'' if not show_options else ' (' + ', '.join([cls.name for cls in load_options[fmt] if cls.is_supported and cls != IO.load_cls[fmt]]) + ')'}")
        
        print("\n export:")
        
        for fmt in IO.export_cls:
            print(f"    {fmt}: {IO.export_cls[fmt].name if IO.export_cls[fmt] else '-'}{'' if not show_options else ' (' + ', '.join([cls.name for cls in export_options[fmt] if cls.is_supported and cls != IO.export_cls[fmt]]) + ')'}")
            
        print()
    
    # TODO let user know what other options are available
    @staticmethod
    def set_io(action, class_name, fmt=None):
        # allows user to switch I/O instruments
        if action == "play":
            IO.play_cls = _io_alternatives[class_name]
        elif action == "load":
            IO.load_cls[fmt if fmt else "*"] = _io_alternatives[class_name]
        elif action == "export":
            IO.export_cls[fmt if fmt else "*"] = _io_alternatives[class_name]
    
    
    @staticmethod
    def play(audio, **kwargs):
        return IO.play_cls.playback(audio, **kwargs)
    
    
    
    @staticmethod
    def export_WAV(*args, **kwargs):
        IO.export_cls["wav"].export_WAV(*args, **kwargs)
    
    @staticmethod
    def export_AIFF(*args, **kwargs):
        IO.export_cls["aiff"].export_AIFF(*args, **kwargs)
    
    @staticmethod
    def export_file(*args, **kwargs):
        IO.export_cls["*"].export_file(*args, **kwargs)
    
    # TODO find the correct place to ensure file exists in the first place
    @staticmethod
    def WAV_to_Audio(*args, **kwargs):
        return IO.load_cls["wav"].WAV_to_Audio(*args, **kwargs)
    
    @staticmethod
    def AIFF_to_Audio(*args, **kwargs):
        return IO.load_cls["aiff"].AIFF_to_Audio(*args, **kwargs)
    
    @staticmethod
    def file_to_Audio(*args, **kwargs):
        return IO.load_cls["*"].file_to_Audio(*args, **kwargs)
    
    
    
    ###
    @staticmethod
    def cleanup():
        """
        In some cases Gensound can't immediately perform cleanup on converted files
        (for example, since they are being played at the moment!)
        This allows the user to manually instruct Gensound to delete them.
        However, nothing is guaranteed, as some hardwares seem decide to keep locking
        the files until the program returns.
        """
        import os
        
        deleted = 0
        
        for filename in _temp_files:
            try:
                os.remove(filename)
                deleted += 0
            except:
                ...
        
        print(f"Deleted {deleted} files out of {len(_temp_files)}.")
                    














### for testing purposes; outputs WAV and logs the cade that generated it ####

def export_test(audio, func=None, byte_width=2, max_amplitude=1):
    if not hasattr(audio, "buffer"):
        audio._prepare_buffer(byte_width, max_amplitude)
    
    assert inspect.stack()[1].function == func.__name__, "logging names don't match!!!"
    
    timestamp = time.strftime('%Y-%b-%d_%H%M', time.localtime())
    _IO_wave.export_WAV("../output/export_{timestamp}_{caller.function}.wav".format( 
                   timestamp = timestamp,
                   caller = inspect.stack()[1]),
                audio)
    
    if func is None:
        return
    
    with open("../output/_export_log.txt", "a") as file:
        # TODO make sure not to overwrite
        file.write("++++++ {} ++++++\n------ {} ------\n\n{}\n\n".format(
                                                               func.__name__,
                                                               timestamp,
                                                               inspect.getsource(func)))



