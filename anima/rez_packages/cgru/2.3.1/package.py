# -*- coding: utf-8 -*-

name = "cgru"

version = "2.3.1"

author = [
    "Erkan Ozgur Yilmaz",
]

uuid = "3e38a9bf0e364a2995ecacfa30bd4811"

description = "CGRU/Afanasy Package"


variants = [
    ["platform-linux", "maya"],
    ["platform-linux", "houdini"],
]

build_command = "python {root}/../build.py {install}"


def commands():
    import os

    # Various applications uses own python:
    unsetenv("PYTHONHOME")

    # Set CGRU root:
    env.CGRU_LOCATION.set("/opt/cgru")

    # Add CGRU bin to path:
    env.PATH.prepend("${CGRU_LOCATION}/bin")

    # Add software to PATH:
    env.PATH.prepend("${CGRU_LOCATION}/software_setup/bin")

    # Python module path:
    env.CGRU_PYTHON = "${CGRU_LOCATION}/lib/python"
    env.PYTHONPATH.prepend("${CGRU_PYTHON}")

    # Get CGRU version:
    env.CGRU_VERSION = "{}.{}.{}".format(
        env.REZ_CGRU_MAJOR_VERSION,
        env.REZ_CGRU_MINOR_VERSION,
        env.REZ_CGRU_PATCH_VERSION,
    )

    # Set Afanasy root:
    env.AF_ROOT = "${CGRU_LOCATION}/afanasy"
    env.PATH.prepend("${AF_ROOT}/bin")

    # Python module path:
    env.AF_PYTHON = "${AF_ROOT}/python"
    env.PYTHONPATH.prepend(env.AF_PYTHON)

    if "CGRU_PYTHONEXE" not in env.keys():
        env.CGRU_PYTHONEXE = "python"
        python_dir = "${CGRU_LOCATION}/python"
        if os.path.isdir(os.path.expandvars(python_dir)):
            print(f"Using CGRU Python: {python_dir}")
            env.PYTHONHOME = python_dir
            env.PATH.prepend(f"{python_dir}/bin")
            env.CGRU_PYTHONDIR = f"{python_dir}"
            pythonexe = f"{python_dir}/bin/python3"
            if os.path.isfile(pythonexe):
                env.CGRU_PYTHONEXE = f"{pythonexe}/bin/python3"
        else:
            env.CGRU_PYTHONEXE = "python3"

    sip = "$CGRU_LOCATION/utilities/python/sip"
    if os.path.isdir(os.path.expandvars(sip)):
        env.PYTHONPATH.prepend(f"{sip}")

    pyqt = "$CGRU_LOCATION/utilities/python/pyqt"
    if os.path.isdir(os.path.expandvars(pyqt)):
        env.PYTHONPATH.prepend(f"{pyqt}")

    # Maya
    if "maya" in this.root:
        # CGRU for Maya add-ons location, override it,
        # or simple launch from current folder as an example
        env.MAYA_CGRU_LOCATION = "$CGRU_LOCATION/plugins/maya"
        env.PYTHONPATH.prepend("${MAYA_CGRU_LOCATION}")

        # Locate Maya:
        env.MAYA_LOCATION = "/usr/autodesk/maya{}".format(
            env.REZ_MAYA_MAJOR_VERSION
        )
        env.MAYA_VERSION = env.REZ_MAYA_MAJOR_VERSION
        env.MAYA_EXEC = "${MAYA_LOCATION}/bin/maya${MAYA_VERSION}"
        print(f"MAYA: {env.MAYA_EXEC}")
        print(f"MAYA_VERSION: {env.MAYA_VERSION}")

        # The name of Maya main window menu
        env.MAYA_CGRU_MENUS_NAME = "CGRU"

        # Set more standard (to all distributions) temporary directory:
        env.TMPDIR = "/tmp"

        # Add CGRU icons to Maya:
        env.XBMLANGPATH.prepend("${MAYA_CGRU_LOCATION}/icons/%B")
        # Add CGRU scripts to Maya scripts path:
        env.MAYA_SCRIPT_PATH.prepend("${MAYA_CGRU_LOCATION}/mel/AETemplates")
        # Add CGRU plugins to Maya plugins path:
        env.MAYA_PLUG_IN_PATH.prepend("${MAYA_CGRU_LOCATION}/mll/${MAYA_VERSION}")

        # Add Afanasy scripts to Maya:
        env.MAYA_SCRIPT_PATH.prepend("${MAYA_CGRU_LOCATION}/afanasy")

        env.APP_DIR = "${MAYA_LOCATION}"
        env.APP_EXE = "${MAYA_EXEC}"

    # Houdini
    if "houdini" in this.root:
        env.APP_DIR = "/opt/hfs{}.{}.{}".format(
            env.REZ_HOUDINI_MAJOR_VERSION,
            env.REZ_HOUDINI_MINOR_VERSION,
            env.REZ_HOUDINI_PATCH_VERSION,
        )
        # Setup CGRU houdini scripts location:
        env.HOUDINI_CGRU_PATH = "$CGRU_LOCATION/plugins/houdini"

        # Set Python path to afanasy submission script:
        env.PYTHONPATH.prepend("$HOUDINI_CGRU_PATH")

        # Define OTL scan path:
        env.HOUDINI_CGRU_OTLSCAN_PATH.append("$HIH/otls")
        env.HOUDINI_CGRU_OTLSCAN_PATH.append("$HOUDINI_CGRU_PATH")
        env.HOUDINI_CGRU_OTLSCAN_PATH.append("$HH/otls")

        # Create or add to exist OTL scan path:
        if "HOUDINI_OTLSCAN_PATH" not in env.keys():
            env.HOUDINI_OTLSCAN_PATH = "$HOUDINI_CGRU_OTLSCAN_PATH"
        else:
            env.HOUDINI_OTLSCAN_PATH.prepend("${HOUDINI_CGRU_OTLSCAN_PATH}")

        env.APP_EXE = "houdini"