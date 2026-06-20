# SPDX-License-Identifier: GPL-2.0+

from importlib import metadata

try:
    __version__ = metadata.version("pyMesa")
except metadata.PackageNotFoundError:
    # package is not installed
    pass
