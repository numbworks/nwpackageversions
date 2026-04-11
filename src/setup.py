'''Contains packaging instructions.'''

# GLOBAL MODULES
from setupinfo import CLI_NAME, PROJECT_VERSION, PROJECT_AUTHOR, PROJECT_URL, LIBRARY_NAME, LIBRARY_DESCRIPTION
from setuptools import setup

# SETUP
if __name__ == "__main__":
    setup(
        name = LIBRARY_NAME,
        version = PROJECT_VERSION,
        description = LIBRARY_DESCRIPTION,
        author = PROJECT_AUTHOR,
        url = PROJECT_URL,
        py_modules = [ LIBRARY_NAME, CLI_NAME, "setupinfo" ],
        install_requires = [ 
            "requests==2.32.3",
            "lxml==5.3.0"
		],
        python_requires = ">=3.12",
        license = "MIT",
        entry_points = {
            'console_scripts': [
                f'{CLI_NAME} = {CLI_NAME}:main',
            ],
        }
    )