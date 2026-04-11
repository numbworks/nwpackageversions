'''
A CLI application built around nwpackageversions.

Alias: nwpver
'''

# GLOBAL MODULES
import os
from argparse import ArgumentParser, Namespace
from typing import Final, Optional, Tuple

# LOCAL/NW MODULES
from nwpackageversions import RequirementChecker, RuntimeChecker
from setupinfo import CLI_NAME, CLI_DESCRIPTION

# GENERIC CLASSES
# CONSTANTS
# STATIC CLASSES
class _MessageCollectionAsciiBannerManager():

    '''Collects all the messages used for logging and for the exceptions.'''

    @staticmethod
    def provided_version_empty_whitespace() -> str:
        return "The provided 'version' is empty or whitespace."
class _MessageCollection(
    _MessageCollectionAsciiBannerManager):

    '''Collects all the messages used for logging and for the exceptions.'''

    pass

# CLASSES
class AsciiBannerManager:

    """
        Creates the ASCII banner for the provided library's version.

        The figlet can be generated using 
            - 'http://www.network-science.de/ascii/' (font: "banner3-D", width: 120)
            - 'https://www.askapache.com/online-tools/figlet-ascii/'.
    """

    def __validate(self, version: str) -> None:
        
        """Validates the provided 'version'."""

        if not version or not version.strip():
            raise ValueError(_MessageCollection.provided_version_empty_whitespace())
    def __create_figlet(self) -> tuple:
        
        """Returns a tuple containing the figlet and its width."""
        
        lines : list[str] = [
            "'##::: ##:'##:::::'##:'########::'##::::'##:'########:'########::",
            " ###:: ##: ##:'##: ##: ##.... ##: ##:::: ##: ##.....:: ##.... ##:",
            " ####: ##: ##: ##: ##: ##:::: ##: ##:::: ##: ##::::::: ##:::: ##:",
            " ## ## ##: ##: ##: ##: ########:: ##:::: ##: ######::: ########::",
            " ##. ####: ##: ##: ##: ##.....:::. ##:: ##:: ##...:::: ##.. ##:::",
            " ##:. ###: ##: ##: ##: ##:::::::::. ## ##::: ##::::::: ##::. ##::",
            " ##::. ##:. ###. ###:: ##::::::::::. ###:::: ########: ##:::. ##:",
            "..::::..:::...::...:::..::::::::::::...:::::........::..:::::..::"
        ]

        return (os.linesep.join(lines), len(lines[0]))
    def __create_frame(self, version: str, max_length: int) -> tuple:
        
        """Returns a tuple containing the frame of the figlet."""
        
        version_token : str = f"Version: {version}"
        
        margin_length : int = 5
        total_length : int = max_length - len(version_token) - margin_length

        top_line : str = "*" * max_length
        bottom_line : str = f"{top_line[:total_length]}{version_token}{'*' * margin_length}"

        return (top_line, bottom_line)

    def create(self, version: str) -> str:
        
        """Creates the formatted ASCII banner with a versioned frame."""
        
        self.__validate(version)

        figlet, max_length = self.__create_figlet()
        top_line, bottom_line = self.__create_frame(version, max_length)

        ascii_banner : str = os.linesep.join([
            top_line,
            figlet,
            bottom_line,
            ""
        ])

        return ascii_banner

# MAIN
def main(): pass # CLIManager().run_and_log()

if __name__ == "__main__":
    main()
