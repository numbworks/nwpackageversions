'''Contains packaging information about nwpackageversions.py.'''

# GLOBAL MODULES
from setuptools import setup

# INFORMATION
MODULE_ALIAS : str = "nwpv"
MODULE_NAME : str = "nwpackageversions"
MODULE_VERSION : str = "1.0.0"

# SETUP
setup(
    name = MODULE_NAME,
    version = MODULE_VERSION,
    description = "A module that helps with retrieving package information from PyPi.org.",
    author = "numbworks",
    url = "https://github.com/numbworks/nwpackageversions",
    py_modules = [ MODULE_NAME ],
    install_requires = [
        "requests==2.31.0"
    ],
    python_requires = ">=3.12",
    license = "MIT"
)