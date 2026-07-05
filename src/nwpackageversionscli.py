'''
A CLI application built around nwpackageversions.

Alias: nwpver
'''

# GLOBAL MODULES
import os
import re
import subprocess
from argparse import _SubParsersAction, ArgumentParser, ArgumentTypeError, Namespace
from re import Match
from shutil import get_terminal_size
from subprocess import CompletedProcess
from typing import Any, Callable, Final, Optional, Tuple

# LOCAL/NW MODULES
from nwpackageversions import RequirementChecker, RuntimeChecker, LambdaCollection, DEFAULT
from setupinfo import CLI_DESCRIPTION, PROJECT_VERSION

# GENERIC CLASSES
# CONSTANTS
class CLISTRING:

    '''Collects all the CLI-related strings.'''

    COMMAND_DEST : Final[str] = "command"
    COMMAND_REQUIRED : Final[bool] = True
    COMMAND_ARGS : dict[str, Any] = { "dest": COMMAND_DEST, "required": COMMAND_REQUIRED }

    COMMAND_RUNTIME_NAME : Final[str] = "runtime"
    COMMAND_RUNTIME_HELP : Final[str] = "Checks the status of the Python runtime."

    COMMAND_REQUIREMENTS_NAME : Final[str] = "requirements"
    COMMAND_REQUIREMENTS_HELP : Final[str] = "Checks the status of the required packages."

    OPTION_REQUIRED_FLAGS : Final[list[str]] = ["--required"]
    OPTION_REQUIRED_DEST : Final[str] = "required"
    OPTION_REQUIRED_REQUIRED : Final[bool] = True
    OPTION_REQUIRED_HELP : Final[str] = "The required Python version (e.g., 3.12.5)."

    OPTION_FILEPATH_FLAGS : Final[list[str]] = ["--file_path"]
    OPTION_FILEPATH_DEST : Final[str] = "file_path"
    OPTION_FILEPATH_REQUIRED : Final[bool] = True
    OPTION_FILEPATH_HELP : Final[str] = "The path to the file containing package requirements."

    OPTION_ONLYSTABLERELEASES_FLAGS : Final[list[str]] = ["--only_stable_releases"]
    OPTION_ONLYSTABLERELEASES_DEST : Final[str] = "only_stable_releases"
    OPTION_ONLYSTABLERELEASES_REQUIRED : Final[bool] = False
    OPTION_ONLYSTABLERELEASES_DEFAULT : Final[bool] = DEFAULT.ONLY_STABLE_RELEASES
    OPTION_ONLYSTABLERELEASES_HELP : Final[str] = "Whether to consider only stable releases or not."

    OPTION_WAITINGTIME_FLAGS : Final[list[str]] = ["--waiting_time"]
    OPTION_WAITINGTIME_DEST : Final[str] = "waiting_time"
    OPTION_WAITINGTIME_TYPE : type = int
    OPTION_WAITINGTIME_DEFAULT : Final[int] = DEFAULT.WAITING_TIME
    OPTION_WAITINGTIME_HELP : Final[str] = "The waiting time between requests (in seconds)."

# STATIC CLASSES
class _MessageCollectionAsciiBannerManager():

    '''Collects all the messages used for logging and for the exceptions.'''

    @staticmethod
    def provided_version_empty_whitespace() -> str:
        return "The provided 'version' is empty or whitespace."
class _MessageCollectionCLIValidator():

    '''Collects all the messages used for logging and for the exceptions used by CLIValidator.'''

    @staticmethod
    def provided_required_not_valid(required : str) -> str:
        return f"The provided 'required' ('{required}') is not a valid version."
class _MessageCollection(
    _MessageCollectionAsciiBannerManager,
    _MessageCollectionCLIValidator):

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

    def create_standard(self, version : str) -> str:
        
        """Creates the standard ASCII banner."""
        
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
    def create_mini(self, version : str) -> str:

        """
            Creates the mini ASCII banner:
            
                *****************
                * NWPVER v1.0.0 *
                *****************
        """

        self.__validate(version)

        assembly_name : str = "NWPVER"
        middle_line : str = f"* {assembly_name} v{version} *"
        
        top_line : str = "*" * len(middle_line)
        bottom_line : str = top_line

        ascii_banner : str = os.linesep.join([
            top_line,
            middle_line,
            bottom_line,
            ""
        ])

        return ascii_banner
    def create(self, version : str, terminal_width : int) -> str:

        """Creates either a standard or mini ASCII banner depending on the terminal width."""
        
        _, max_length = self.__create_figlet()

        if max_length <= terminal_width:
            return self.create_standard(version)
        else:
            return self.create_mini(version)
class TerminalWindowManager:

    '''Handles terminal window size.'''

    __shutil_width_function : Callable[[], Optional[int]]
    __stty_width_function : Callable[[], Optional[int]]

    cutoff_width : Final[int] = 70

    @staticmethod
    def default_shutil_width_function() -> Optional[int]:

        """Get terminal width using shutil (multi-platform)."""

        try:

            terminal_width : int = get_terminal_size().columns

            return terminal_width
        
        except:
            return None

    @staticmethod
    def default_stty_width_function() -> Optional[int]:

        """Get terminal width using stty command (Linux)."""

        try:

            process : CompletedProcess[str] = subprocess.run(
                ["/bin/sh", "-c", "stty size | cut -d' ' -f2"],
                capture_output = True,
                text = True,
                check = False,
            )

            stty_output : str = process.stdout.strip()
            terminal_width : int = int(stty_output)

            if terminal_width >= 0:
                return terminal_width

            return None
        except:
            return None

    def __init__(
        self,
        shutil_width_function : Optional[Callable[[], Optional[int]]] = None,
        stty_width_function : Optional[Callable[[], Optional[int]]] = None,
    ) -> None:
        
        if shutil_width_function is None:
            shutil_width_function = self.default_shutil_width_function
        
        if stty_width_function is None:
            stty_width_function = self.default_stty_width_function

        self.__shutil_width_function = shutil_width_function
        self.__stty_width_function = stty_width_function

    def get_or_cutoff(self) -> int:

        terminal_width : Optional[int] = self.__shutil_width_function()

        if terminal_width is None:
            terminal_width = self.__stty_width_function()

        if terminal_width is None:
            terminal_width = self.cutoff_width

        return terminal_width
class CLIValidator:

    '''Handles CLI argument validation.'''

    def validate_required(self, required: str) -> Tuple[int, int, int]:

        '''Validates that the version string can be parsed into a Tuple[int, int, int].'''

        pattern : str = r"^(\d+)\.(\d+)\.(\d+)$"
        match : Optional[Match] = re.match(pattern, required)

        if not match:
            raise ArgumentTypeError(_MessageCollection.provided_required_not_valid(required))

        item_1, item_2, item_3 = map(int, match.groups())
        version_tpl : Tuple[int, int, int] = (item_1, item_2, item_3)

        return version_tpl
class APFactory():

    '''Encapsulates all the logic related to the creation of a custom instance of argparse.ArgumentParser.'''

    __cli_validator : CLIValidator

    def __init__(self, cli_validator : CLIValidator = CLIValidator()) -> None:
        self.__cli_validator = cli_validator

    def create(self) -> ArgumentParser:

        '''
            Creates a custom instance of argparse.ArgumentParser.

            The "prog" argument is not provided in order to make the "usage" statement  dynamic:

                usage: nwpackageversionscli [-h] {runtime,requirements} ...
                usage: nwpver [-h] {runtime,requirements} ...
        '''

        argument_parser : ArgumentParser = ArgumentParser(description = CLI_DESCRIPTION)
        root : _SubParsersAction = argument_parser.add_subparsers(**CLISTRING.COMMAND_ARGS)

        runtime_parser : ArgumentParser = root.add_parser(
            name = CLISTRING.COMMAND_RUNTIME_NAME, 
            help = CLISTRING.COMMAND_RUNTIME_HELP)
        
        runtime_parser.add_argument(
            *CLISTRING.OPTION_REQUIRED_FLAGS,
            dest = CLISTRING.OPTION_REQUIRED_DEST,
            required = CLISTRING.OPTION_REQUIRED_REQUIRED,
            help = CLISTRING.OPTION_REQUIRED_HELP,
            type = self.__cli_validator.validate_required)

        requirements_parser : ArgumentParser = root.add_parser(
            name = CLISTRING.COMMAND_REQUIREMENTS_NAME, 
            help = CLISTRING.COMMAND_REQUIREMENTS_HELP)

        requirements_parser.add_argument(
            *CLISTRING.OPTION_FILEPATH_FLAGS,
            dest = CLISTRING.OPTION_FILEPATH_DEST,
            required = CLISTRING.OPTION_FILEPATH_REQUIRED,
            help = CLISTRING.OPTION_FILEPATH_HELP)

        requirements_parser.add_argument(
            *CLISTRING.OPTION_ONLYSTABLERELEASES_FLAGS,
            dest = CLISTRING.OPTION_ONLYSTABLERELEASES_DEST,
            default = CLISTRING.OPTION_ONLYSTABLERELEASES_DEFAULT,
            help = CLISTRING.OPTION_ONLYSTABLERELEASES_HELP)

        requirements_parser.add_argument(
            *CLISTRING.OPTION_WAITINGTIME_FLAGS,
            dest = CLISTRING.OPTION_WAITINGTIME_DEST,
            type = CLISTRING.OPTION_WAITINGTIME_TYPE,
            default = CLISTRING.OPTION_WAITINGTIME_DEFAULT,
            help = CLISTRING.OPTION_WAITINGTIME_HELP)

        return argument_parser
class CLIManager():

    '''Collects all the logic related to the CLI management.'''

    __ap_factory : APFactory
    __ascii_banner_manager : AsciiBannerManager
    __runtime_checker : RuntimeChecker
    __requirement_checker : RequirementChecker
    __tw_manager : TerminalWindowManager
    __logging_function : Callable[[str], None]

    def __init__(
        self, 
        ap_factory : APFactory = APFactory(), 
        ascii_banner_manager : AsciiBannerManager = AsciiBannerManager(),
        runtime_checker : RuntimeChecker = RuntimeChecker(),
        requirement_checker : RequirementChecker = RequirementChecker(),
        tw_manager : TerminalWindowManager = TerminalWindowManager(),
        logging_function : Callable[[str], None] = LambdaCollection.logging_function()) -> None:
        
        self.__ap_factory = ap_factory
        self.__ascii_banner_manager = ascii_banner_manager
        self.__runtime_checker = runtime_checker
        self.__requirement_checker = requirement_checker
        self.__tw_manager = tw_manager
        self.__logging_function = logging_function

    def __log_ascii_banner(self) -> None:

        '''Logs the ascii banner.'''

        terminal_width : int = self.__tw_manager.get_or_cutoff()
        ascii_banner : str = self.__ascii_banner_manager.create(PROJECT_VERSION, terminal_width)

        self.__logging_function("")
        self.__logging_function(ascii_banner)
    def __log_namespace(self, args : Namespace):

        '''Logs the provided args.'''

        for key, value in vars(args).items():
            self.__logging_function(f"{key}: '{value}'")
            
        self.__logging_function("")

    def parse(self) -> None:

        '''
            Parses arguments and dispatches the logic to the appropriate checker.

            The SystemExit exception occurs when the command subparser is required but issn't provided.
            SystemExit doesn't inherit from Exception and has no message, therefore we need to handle it accordingly.
        '''

        try:

            self.__log_ascii_banner()

            argument_parser : ArgumentParser = self.__ap_factory.create()
            args : Namespace = argument_parser.parse_args()

            self.__log_namespace(args)

            if args.command == CLISTRING.COMMAND_RUNTIME_NAME:
                status : str = self.__runtime_checker.try_get_status(required = args.required)
                self.__logging_function(status)
            
            elif args.command == CLISTRING.COMMAND_REQUIREMENTS_NAME:
                status = self.__requirement_checker.try_get_status(
                    file_path = args.file_path,
                    only_stable_releases = args.only_stable_releases,
                    waiting_time = args.waiting_time)
                self.__logging_function(status)
            
        except (Exception, SystemExit) as e:

            if not isinstance(e, SystemExit):
                self.__logging_function(str(e))

# MAIN
def main(): CLIManager().parse()

if __name__ == "__main__":
    main()