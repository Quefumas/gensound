# -*- coding: utf-8 -*-


_supported = set()

try:
    import pkg_resources
    # print("loading supported modules...")
    # uncomment to ensure this code indeed only runs once
    _supported = {pkg.key for pkg in pkg_resources.working_set}
except ModuleNotFoundError:
    print("pkg_resources not installed; can't ascertain support of external modules.")
