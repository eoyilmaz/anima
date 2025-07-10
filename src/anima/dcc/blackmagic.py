"""BlackMagic Design DaVinci Resolve and Fusion API wrapper."""


def get_resolve():
    import DaVinciResolveScript
    return DaVinciResolveScript.scriptapp("Resolve")


def get_fusion():
    import fusionscript
    return fusionscript.scriptapp("Fusion")
