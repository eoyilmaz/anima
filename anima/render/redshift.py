import os


class RedShiftTextureProcessor(object):
    """A wrapper for the ``redshiftTextureProcessor.exe``

    TextureProcessor <inputfile> [options]

    Options are:
            -l              Force linear gamma (recommended for floating point textures)
            -s              Force SRGB gamma (recommended for integer textures)
            (Note the default gamma operation is as follows: -l for floating point textures and -s for integer textures)
            -p              Photometric IES data (for IES profile types)
            -wx             Used as a tiled texture with wrapping/repeats
            -wy             Used as a tiled texture with wrapping/repeats
            -isphere        Image Based Light - Sphere projection
            -ihemisphere    Image Based Light - Hemisphere projection
            -imirrorball    Image Based Light - Mirrorball projection
            -iangularmap    Image Based Light - Angular Map projection
            -ocolor         Sprite Cut-Out Map opacity from color intensity
            -oalpha         Sprite Cut-Out Map opacity from alpha
            -noskip         Disable the skipping of already converted textures if the processor thinks no data has changed
            -r              Recursively process textures in sub directories
            -log            Enable logging to log file
    """

    executable = os.path.join(
        os.environ.get("REDSHIFT_COREDATAPATH", ""), "bin/redshiftTextureProcessor"
    )

    def __init__(
        self,
        input_file_full_path,
        l=None,
        s=None,
        p=None,
        wx=None,
        wy=None,
        isphere=None,
        ihemisphere=None,
        imirrorball=None,
        iangularmap=None,
        ocolor=None,
        oalpha=None,
        noskip=False,
        r=None,
        log=None,
    ):

        self.input_file_full_path = os.path.normpath(
            os.path.expandvars(input_file_full_path)
        ).replace("\\", "/")
        self.files_to_process = []
        self.expand_tiles()
        self.noskip = noskip

    def expand_tiles(self):
        """expands any tiles and returns a list of file paths"""
        if "<" in self.input_file_full_path:
            # replace any <U> and <V> with an *
            self.input_file_full_path = (
                self.input_file_full_path.replace("<U>", "*")
                .replace("<V>", "*")
                .replace("<UDIM>", "*")
            )

        import glob

        self.files_to_process = glob.glob(self.input_file_full_path)

    def convert(self):
        """converts the given input_file to an rstexbin"""
        processed_files = []

        import subprocess
        from anima.utils.progress import ProgressManager

        pdm = ProgressManager()
        caller = pdm.register(len(self.files_to_process), title="Converting Textures")
        for file_path in self.files_to_process:
            command = '%s "%s"' % (self.executable, file_path)
            rsmap_full_path = "%s.rstexbin" % os.path.splitext(file_path)[0]

            # os.system(command)
            if os.name == "nt":
                proc = subprocess.Popen(
                    command, creationflags=subprocess.SW_HIDE, shell=True
                )
            else:
                proc = subprocess.Popen(command, shell=True)
            proc.wait()

            processed_files.append(rsmap_full_path)
            caller.step()
        caller.end_progress()

        return processed_files
