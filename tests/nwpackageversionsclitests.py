# GLOBAL MODULES
import unittest
from argparse import ArgumentParser, ArgumentTypeError, Namespace
from io import StringIO
from parameterized import parameterized
from subprocess import CompletedProcess
from typing import Any, Optional, Tuple
from unittest.mock import MagicMock, Mock, patch

# LOCAL MODULES
import sys, os
sys.path.append(os.path.dirname(__file__).replace('tests', 'src'))
from nwpackageversions import RequirementChecker, RuntimeChecker
from nwpackageversionscli import CLISTRING, APFactory, AsciiBannerManager, _MessageCollection, CLIManager, CLIValidator, TerminalWindowManager

# SUPPORT METHODS
# TEST CLASSES
class AsciiBannerManagerTestCase(unittest.TestCase):

    def test_validate_shouldraisevalueerror_whenversionisnone(self) -> None:

        # Arrange
        # Act, Assert
        with self.assertRaises(ValueError) as context:
            AsciiBannerManager()._AsciiBannerManager__validate(version = None) # type: ignore

        self.assertEqual(_MessageCollection.provided_version_empty_whitespace(), str(context.exception))
    def test_validate_shouldraisevalueerror_whenversioniswhitespace(self) -> None:

        # Arrange
        version : str = " "

        # Act, Assert
        with self.assertRaises(ValueError) as context:
            AsciiBannerManager()._AsciiBannerManager__validate(version = version) # type: ignore

        self.assertEqual(_MessageCollection.provided_version_empty_whitespace(), str(context.exception))
    def test_createfiglet_shouldreturnexpectedmaxlength_wheninvoked(self) -> None:

        # Arrange
        expected : int = 65

        # Act
        _, max_length = AsciiBannerManager()._AsciiBannerManager__create_figlet() # type: ignore

        # Assert
        self.assertEqual(expected, max_length)
    def test_createframe_shouldreturnexpectedtuple_wheninvoked(self) -> None:

        # Arrange
        version : str = "1.0.5"
        max_length : int = 65
        
        expected_top_line : str = "*" * 65
        expected_bottom_line : str = "*" * 46 + "Version: 1.0.5" + "*" * 5

        # Act
        top_line, bottom_line = AsciiBannerManager()._AsciiBannerManager__create_frame(version = version, max_length = max_length) # type: ignore

        # Assert
        self.assertEqual(expected_top_line, top_line)
        self.assertEqual(expected_bottom_line, bottom_line)
    def test_create_shouldcallexpectedprivatemethodsandreturnbanner_wheninvoked(self) -> None:

        # Arrange
        ascii_banner_manager : AsciiBannerManager = AsciiBannerManager()
        version : str = "1.0.5"
        max_lenght : int = 65
        
        figlet_tpl : tuple = ("ascii_art", max_lenght)
        frame_tpl : tuple = ("top_border", "bottom_border")

        with patch.object(ascii_banner_manager, "_AsciiBannerManager__validate") as mocked_validate, \
                patch.object(ascii_banner_manager, "_AsciiBannerManager__create_figlet", return_value = figlet_tpl) as mocked_create_figlet, \
                patch.object(ascii_banner_manager, "_AsciiBannerManager__create_frame", return_value = frame_tpl) as mocked_create_frame:

            # Act
            actual : str = ascii_banner_manager.create(version = version)

            # Assert
            mocked_validate.assert_called_once_with(version)
            mocked_create_figlet.assert_called_once()
            mocked_create_frame.assert_called_once_with(version, max_lenght)

            self.assertIn("top_border", actual)
            self.assertIn("ascii_art", actual)
            self.assertIn("bottom_border", actual)

class TerminalWindowManagerTestCase(unittest.TestCase):

    def test_defaultshutilwidthfunction_shouldreturncolumns_whenshutilissuccessful(self) -> None:

        # Arrange
        expected : int = 80

        with patch("shutil.get_terminal_size") as get_terminal_size:

            get_terminal_size.return_value = os.terminal_size((expected, 24))

            # Act
            actual : Optional[int] = TerminalWindowManager.default_shutil_width_function()

            # Assert
            self.assertEqual(actual, expected)
    def test_defaultshutilwidthfunction_shouldreturnnone_whenexceptionisraised(self) -> None:

        # Arrange
        with patch("nwpackageversionscli.get_terminal_size", side_effect = Exception("Error")):

            # Act
            actual : Optional[int] = TerminalWindowManager.default_shutil_width_function()

            # Assert
            self.assertIsNone(actual)
    
    def test_defaultsttywidthfunction_shouldreturnwidth_whensttyissuccessful(self) -> None:

        # Arrange
        expected : int = 100

        process : Mock = Mock(spec = CompletedProcess)
        process.stdout = f"  {expected}  \n"
        
        with patch("subprocess.run", return_value = process) as mock_run:

            # Act
            actual : Optional[int] = TerminalWindowManager.default_stty_width_function()

            # Assert
            mock_run.assert_called_once_with(
                ["/bin/sh", "-c", "stty size | cut -d' ' -f2"],
                capture_output = True,
                text = True,
                check = False,
            )
            self.assertEqual(actual, expected)
    def test_defaultsttywidthfunction_shouldreturnnone_whensttyreturnsnegative(self) -> None:

        # Arrange
        process : Mock = Mock(spec = CompletedProcess)
        process.stdout = "-10\n"
        
        with patch("subprocess.run", return_value = process):

            # Act
            actual_width : Optional[int] = TerminalWindowManager.default_stty_width_function()

            # Assert
            self.assertIsNone(actual_width)
    def test_defaultsttywidthfunction_shouldreturnnone_whenexceptionisraised(self) -> None:

        # Arrange
        with patch("subprocess.run", side_effect = Exception("Error")):

            # Act
            actual_width : Optional[int] = TerminalWindowManager.default_stty_width_function()

            # Assert
            self.assertIsNone(actual_width)

    def test_init_shouldassignprovidedfunctions_wheninvokedwitharguments(self) -> None:

        # Arrange
        shutil_width_function : Mock = Mock()
        stty_width_function : Mock = Mock()

        # Act
        tw_manager : TerminalWindowManager = TerminalWindowManager(
            shutil_width_function = shutil_width_function,
            stty_width_function = stty_width_function
        )

        # Assert
        self.assertEqual(tw_manager._TerminalWindowManager__shutil_width_function, shutil_width_function)   # type: ignore
        self.assertEqual(tw_manager._TerminalWindowManager__stty_width_function, stty_width_function)       # type: ignore
    def test_init_shouldassigndefaultfunctions_wheninvokedwithoutarguments(self) -> None:

        # Arrange
        tw_manager : TerminalWindowManager = TerminalWindowManager()

        # Assert
        self.assertEqual(tw_manager._TerminalWindowManager__shutil_width_function, TerminalWindowManager.default_shutil_width_function) # type: ignore
        self.assertEqual(tw_manager._TerminalWindowManager__stty_width_function, TerminalWindowManager.default_stty_width_function)     # type: ignore

    def test_getorcutoff_shouldreturnshutilwidth_whenshutilissuccessful(self) -> None:

        # Arrange
        expected : int = 120
        shutil_width_function : Mock = Mock(return_value = expected)
        stty_width_function : Mock = Mock()
        
        tw_manager : TerminalWindowManager = TerminalWindowManager(
            shutil_width_function = shutil_width_function,
            stty_width_function = stty_width_function
        )

        # Act
        actual : int = tw_manager.get_or_cutoff()

        # Assert
        self.assertEqual(actual, expected)
        shutil_width_function.assert_called_once()
        stty_width_function.assert_not_called()
    def test_getorcutoff_shouldreturnsttywidth_whenshutilfailsandsttyissuccessful(self) -> None:

        # Arrange
        expected : int = 90
        shutil_width_function : Mock = Mock(return_value = None)
        stty_width_function : Mock = Mock(return_value = expected)
        
        tw_manager : TerminalWindowManager = TerminalWindowManager(
            shutil_width_function = shutil_width_function,
            stty_width_function = stty_width_function
        )

        # Act
        actual : int = tw_manager.get_or_cutoff()

        # Assert
        self.assertEqual(actual, expected)
        shutil_width_function.assert_called_once()
        stty_width_function.assert_called_once()
    def test_getorcutoff_shouldreturncutoffwidth_whenbothfunctionsfail(self) -> None:

        # Arrange
        shutil_width_function : Mock = Mock(return_value = None)
        stty_width_function : Mock = Mock(return_value = None)
        
        tw_manager : TerminalWindowManager = TerminalWindowManager(
            shutil_width_function = shutil_width_function,
            stty_width_function = stty_width_function
        )

        # Act
        actual : int = tw_manager.get_or_cutoff()

        # Assert
        self.assertEqual(actual, TerminalWindowManager.cutoff_width)
        shutil_width_function.assert_called_once()
        stty_width_function.assert_called_once()
class CLIValidatorTestCase(unittest.TestCase):

    def test_validaterequired_shouldreturntuple_whenversionstringisvalid(self) -> None:

        # Arrange
        required : str = "3.12.5"
        expected : Tuple[int, int, int] = (3, 12, 5)

        # Act
        actual : Tuple[int, int, int] = CLIValidator().validate_required(required = required)

        # Assert
        self.assertEqual(actual, expected)

    @parameterized.expand([
        ["3.12"],
        ["3.12.5.1"],
        ["python3.12.5"],
        ["latest"],
        ["3.12.a"]
    ])
    def test_validaterequired_shouldraiseargumenttypeerror_whenversionstringisinvalid(self, required : str) -> None:

        # Arrange
        validator : CLIValidator = CLIValidator()
        expected : str = _MessageCollection.provided_required_not_valid(required)

        # Act / Assert
        with self.assertRaises(ArgumentTypeError) as context:
            validator.validate_required(required = required)

        self.assertEqual(str(context.exception), expected)
class APFactoryTestCase(unittest.TestCase):

    def test_create_shouldreturnargumentparserwithruntimecommand_wheninvoked(self):

        # Arrange
        cli_validator : MagicMock = MagicMock(spec = CLIValidator)
        ap_factory : APFactory = APFactory(cli_validator = cli_validator)
        version_str : str = "3.12.5"
        expected_version : Tuple[int, int, int] = (3, 12, 5)
        cli_validator.validate_required.return_value = expected_version
        
        args_list : list[str] = [CLISTRING.COMMAND_RUNTIME_NAME, "--required", version_str]

        # Act
        argument_parser : ArgumentParser = ap_factory.create()
        actual : Namespace = argument_parser.parse_args(args_list)

        # Assert
        self.assertEqual(actual.command, CLISTRING.COMMAND_RUNTIME_NAME)
        self.assertEqual(actual.required, expected_version)
        cli_validator.validate_required.assert_called_once_with(version_str)
    def test_create_shouldreturnargumentparserwithrequirementscommandanddefaultvalues_wheninvoked(self):

        # Arrange
        ap_factory : APFactory = APFactory()
        file_path : str = "C:/Dockerfile"
        args_list : list[str] = [CLISTRING.COMMAND_REQUIREMENTS_NAME, "--file_path", file_path]

        # Act
        argument_parser : ArgumentParser = ap_factory.create()
        actual : Namespace = argument_parser.parse_args(args_list)

        # Assert
        self.assertEqual(actual.command, CLISTRING.COMMAND_REQUIREMENTS_NAME)
        self.assertEqual(actual.file_path, file_path)
        self.assertEqual(actual.only_stable_releases, CLISTRING.OPTION_ONLYSTABLERELEASES_DEFAULT)
        self.assertEqual(actual.waiting_time, CLISTRING.OPTION_WAITINGTIME_DEFAULT)
    def test_create_shouldraiseerror_whenrequiredruntimeargumentismissing(self):

        # Arrange
        args_list : list[str] = [CLISTRING.COMMAND_RUNTIME_NAME]
        argument_parser : ArgumentParser = APFactory().create()

        # Act, Assert
        with patch("sys.stderr", new_callable = StringIO):
            with self.assertRaises(SystemExit):
                argument_parser.parse_args(args_list)
class CLIManagerTestCase(unittest.TestCase):

    def test_parse_shouldlogstatusanddispatchtoruntimechecker_whencommandisruntime(self):

        # Arrange
        expected : str = "Runtime Status"
        args : Namespace = Namespace(command = CLISTRING.COMMAND_RUNTIME_NAME, required = (3, 12, 5))
        
        ap_mock : MagicMock = MagicMock(spec = ArgumentParser)
        ap_mock.parse_args.return_value = args
        
        ap_factory : MagicMock = MagicMock(spec = APFactory)
        ap_factory.create.return_value = ap_mock
        
        runtime_checker : MagicMock = MagicMock(spec = RuntimeChecker)
        runtime_checker.try_get_status.return_value = expected
        
        logging_function : MagicMock = MagicMock()
        
        cli_manager : CLIManager = CLIManager(
            ap_factory = ap_factory,
            runtime_checker = runtime_checker,
            logging_function = logging_function
        )

        # Act
        cli_manager.parse()

        # Assert
        runtime_checker.try_get_status.assert_called_once_with(required = args.required)
        logging_function.assert_any_call(expected)
    def test_parse_shouldlogstatusanddispatchtorequirementchecker_whencommandisrequirements(self):

        # Arrange
        expected : str = "Requirements Status"
        args : Namespace = Namespace(
            command = CLISTRING.COMMAND_REQUIREMENTS_NAME, 
            file_path = "C:/Dockerfile", 
            only_stable_releases = True, 
            waiting_time = 5
        )
        
        ap_mock : MagicMock = MagicMock(spec = ArgumentParser)
        ap_mock.parse_args.return_value = args
        
        ap_factory : MagicMock = MagicMock(spec = APFactory)
        ap_factory.create.return_value = ap_mock
        
        requirement_checker : MagicMock = MagicMock(spec = RequirementChecker)
        requirement_checker.try_get_status.return_value = expected
        
        logging_function : MagicMock = MagicMock()
        
        cli_manager : CLIManager = CLIManager(
            ap_factory = ap_factory,
            requirement_checker = requirement_checker,
            logging_function = logging_function
        )

        # Act
        cli_manager.parse()

        # Assert
        requirement_checker.try_get_status.assert_called_once_with(
            file_path = args.file_path,
            only_stable_releases = args.only_stable_releases,
            waiting_time = args.waiting_time
        )
        logging_function.assert_any_call(expected)
    def test_parse_shouldlogexceptionmessage_whenexceptionisraised(self):

        # Arrange
        expected : str = "Unexpected Error"
        ap_factory : MagicMock = MagicMock(spec = APFactory)
        ap_factory.create.side_effect = Exception(expected)
        
        logging_function : MagicMock = MagicMock()
        
        cli_manager : CLIManager = CLIManager(
            ap_factory = ap_factory,
            logging_function = logging_function
        )

        # Act
        cli_manager.parse()

        # Assert
        logging_function.assert_any_call(expected)
    def test_parse_shoulddonothing_whensystemexitoccurs(self):

        # Arrange
        ap_factory : MagicMock = MagicMock(spec = APFactory)
        ap_factory.create.side_effect = SystemExit()
        
        logging_function : MagicMock = MagicMock()
        
        cli_manager : CLIManager = CLIManager(
            ap_factory = ap_factory,
            logging_function = logging_function
        )

        # Act
        cli_manager.parse()

        # Assert
        calls : list[Any] = logging_function.call_args_list

        for call in calls:
            self.assertNotIsInstance(call.args[0], SystemExit)

# MAIN
if __name__ == "__main__":
    result = unittest.main(argv=[''], verbosity=3, exit=False)