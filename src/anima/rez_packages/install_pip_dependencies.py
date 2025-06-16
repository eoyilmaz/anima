import logging
import subprocess

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.DEBUG,
    handlers=[
        logging.StreamHandler(),
        # logging.FileHandler("install_pip_dependencies.log"),
    ],
)
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)

PACKAGES = [
    "exifread",
    "ldap3",
    "pillow",
    "pyside2",
    "pyside6",
    "qtawesome",
    "qtpy",
    "stalker",
    "timecode",
    "usd-core",
]

PYTHON_VERSIONS = [
    "3.8",
    "3.9",
    "3.10",
    "3.11",
    "3.12",
    "3.13",
]


ERROR_STORAGE = []


def run_command(command):
    """Run a command in the shell and returns the output.

    Args:
        command (list): The command to run as a list of strings.
    """
    LOGGER.debug(f"Running command: {' '.join(command)}")
    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    # loop until process finishes and capture stderr output
    stdin_buffer = []
    stderr_buffer = []
    while True:
        stdin = process.stdout.readline()
        stderr = process.stderr.readline()

        if not isinstance(stdin, str):
            stdin = stdin.decode("utf-8", "replace")

        if not isinstance(stderr, str):
            stderr = stderr.decode("utf-8", "replace")

        if (stderr == "" or stdin == "") and process.poll() is not None:
            break

        if stdin != "":
            stdin_buffer.append(stdin.strip())
            LOGGER.info(stdin.strip())

        if stderr != "":
            stderr_buffer.append(stderr.strip())
            LOGGER.info(stderr.strip())

    if process.returncode:
        # there is an error
        LOGGER.debug("There was an error running the command: %s", " ".join(command))
        ERROR_STORAGE.append(
            f"Command: {' '.join(command)}\nError: {''.join(stderr_buffer)}"
        )


def install_pip_dependencies():
    """Install pip dependencies for all specified packages and Python versions."""
    for package in PACKAGES:
        for version in PYTHON_VERSIONS:
            rez_pip_command = [
                "rez-pip",
                "--python-version",
                version,
                "-i",
                package,
            ]
            run_command(rez_pip_command)
    LOGGER.debug("process completed!")


def main():
    """Main function to install pip dependencies."""
    try:
        install_pip_dependencies()
    except Exception as e:
        LOGGER.error(f"An error occurred while installing pip dependencies: {e}")
        raise e
    else:
        if ERROR_STORAGE:
            LOGGER.error("Errors occurred during installation:")
            for error in ERROR_STORAGE:
                LOGGER.error(error)
            raise RuntimeError("Some pip dependencies failed to install.")
        else:
            LOGGER.info("All pip dependencies installed successfully.")


if __name__ == "__main__":
    main()
