# GLOBAL MODULES
from io import StringIO
import unittest
from argparse import ArgumentParser, ArgumentTypeError, Namespace
from parameterized import parameterized
from typing import Optional, Tuple
from unittest.mock import MagicMock, Mock, patch

# LOCAL MODULES
import sys, os
sys.path.append(os.path.dirname(__file__).replace('tests', 'src'))
from nwpackageversionscli import CLISTRING, APFactory, AsciiBannerManager, _MessageCollection, CLIValidator

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

# MAIN
if __name__ == "__main__":
    result = unittest.main(argv=[''], verbosity=3, exit=False)