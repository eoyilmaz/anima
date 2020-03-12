import os
import imp
import sys


def get_bmd():
    """this routine is a modified version of DaVinciResolveScript.py from
    BlackMagic Design
    """
    bmd = None
    try:
        import fusionscript as bmd
    except ImportError:
        # Look for installer based environment variables:
        import os
        lib_path = os.getenv("RESOLVE_SCRIPT_LIB")
        if lib_path:
            try:
                bmd = imp.load_dynamic("fusionscript", lib_path)
            except ImportError:
                pass
        if not bmd:
            # Look for default install locations:
            ext = ".so"
            if sys.platform.startswith("darwin"):
                path = "/Applications/DaVinci Resolve/DaVinci Resolve.app/Contents/Libraries/Fusion/"
            elif sys.platform.startswith("win") or sys.platform.startswith("cygwin"):
                ext = ".dll"
                path = "C:\\Program Files\\Blackmagic Design\\DaVinci Resolve\\"
            elif sys.platform.startswith("linux"):
                path = "/opt/resolve/libs/Fusion/"

            try:
                bmd = imp.load_dynamic("fusionscript", path + "fusionscript" + ext)
            except ImportError:
                pass

    if bmd:
        sys.modules[__name__] = bmd
        return bmd
    else:
        raise ImportError("Could not locate module dependencies")


def get_resolve():
    bmd = get_bmd()
    return bmd.scriptapp("Resolve")


def get_fusion():
    bmd = get_bmd()
    return bmd.scriptapp("Fusion")
