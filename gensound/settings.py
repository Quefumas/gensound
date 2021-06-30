# -*- coding: utf-8 -*-


_supported = set()
_supported_bin = set()

def get_supported_modules():
    try:
        import pkg_resources
        global _supported
        # print("loading supported modules...")
        # uncomment to ensure this code indeed only runs once
        _supported = {pkg.key for pkg in pkg_resources.working_set}
    except ModuleNotFoundError:
        print("pkg_resources not installed; can't ascertain support of external modules.")

def has_binary(name):
    # tests if a binary is recognizable by system shell
    try:
        import subprocess
        
        process = subprocess.Popen(name, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        out, err = process.communicate(None)
        
        _supported_bin.add(name)
    except:
        ...




get_supported_modules() # find installed libraries (optional requirements for I/O, computation, filters, etc.)
has_binary("ffmpeg") # find whether ffmpeg is installed


