import sys


def get_bmd():
    """this routine is directly from BlackMagic
    """
    try:
        # The PYTHONPATH needs to be set correctly for this import statement to work.
        # An alternative is to import the DaVinciResolveScript by specifying absolute path (see ExceptionHandler logic)
        import DaVinciResolveScript as bmd
    except ImportError:
        expected_path = ''
        if sys.platform.startswith("darwin"):
            expected_path = \
                "/Library/Application Support/Blackmagic Design/DaVinci Resolve/Developer/Scripting/Modules/"
        elif sys.platform.startswith("win") or sys.platform.startswith("cygwin"):
            import os
            expected_path = os.path.normpath(
                os.path.join(
                    os.environ['PROGRAMDATA'],
                    "Blackmagic Design/DaVinci Resolve/Support/Developer/Scripting/Modules/"
                )
            )
        elif sys.platform.startswith("linux"):
            expected_path = "/opt/resolve/libs/Fusion/Modules/"

        # check if the default path has it...
        print("Unable to find module DaVinciResolveScript from $PYTHONPATH - trying default locations")
        try:
            import imp
            print('Trying to import DaVinciResolveScript!')
            print('expected_path: %s' % expected_path)
            bmd = imp.load_source('DaVinciResolveScript', expected_path + "DaVinciResolveScript.py")
        except ImportError:
            # No fallbacks ... report error:
            print("Unable to find module DaVinciResolveScript - please ensure that the module "
                  "DaVinciResolveScript is discoverable by python")
            print("For a default DaVinci Resolve installation, the module is expected to be "
                  "located in: %s" % expected_path)
            sys.exit()

    return bmd


def get_resolve():
    bmd = get_bmd()
    return bmd.scriptapp("Resolve")


def get_fusion():
    bmd = get_bmd()
    return bmd.scriptapp("Fusion")
