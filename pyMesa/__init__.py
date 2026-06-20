import pathlib
import os

from .version import __version__

if "MESA_DIR" not in os.environ:
    raise ValueError("Must set MESA_DIR environment variable")
else:
    MESA_DIR = os.environ.get("MESA_DIR")

if pathlib.Path(MESA_DIR).joinpath("build").exists():
    # Post 2026 versions
    from .pyMesaUtils_2026 import *
else:
    # Older MESA's pre 2026
    from .pyMesaUtils_pre2026 import *
