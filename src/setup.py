'''Contains packaging information about nwpackageversions.py.'''

# GLOBAL MODULES
from setuptools import setup

# INFORMATION
MODULE_ALIAS : str = "nwpv"
MODULE_NAME : str = "nwpackageversions"
MODULE_VERSION : str = "1.8.2"

# SETUP
if __name__ == "__main__":
    setup(
        name = MODULE_NAME,
        version = MODULE_VERSION,
        description = "A library that helps with retrieving package information from PyPi.org and comparing them with what you have installed locally.",
        author = "numbworks",
        url = f"https://github.com/numbworks/{MODULE_NAME}",
        py_modules = [ MODULE_NAME ],
        install_requires = [
            "requests==2.32.3",
            "lxml==5.3.0"
        ],
        python_requires = ">=3.12",
        license = "MIT"
    )