# GLOBAL MODULES
import os
import subprocess
import sys
import unittest
from datetime import datetime
from parameterized import parameterized
from requests import Response
from subprocess import CompletedProcess
from time import time
from typing import Any, Literal, Optional, Callable, Tuple, cast
from unittest.mock import Mock, patch, mock_open, MagicMock

# LOCAL MODULES
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))
from nwpackageversions import _MessageCollection, Badge, BasicFormatter, Formatter, LSession, LambdaCollection
from nwpackageversions import LocalPackageLoader, Package, RuntimeChecker, PyPiBadgeFetcher, Validator
from nwpackageversions import PyPiReleaseFetcher, RequirementChecker, RequirementDetail, RequirementSummary
from nwpackageversions import XMLItem, Release, FSession, JsonFormatter

# SUPPORT METHODS
class ObjectMother():

    '''Collects all the DTOs required by the unit tests.'''

    @staticmethod
    def get_package_1() -> Package:

        package_1 : Package = Package(name = "black", version = "22.12.0")

        return package_1
    @staticmethod
    def get_release_1() -> Release:

        release_1 : Release = Release(package_name = "black", version = "22.12.0", date = datetime(2024, 5, 15))

        return release_1
    @staticmethod
    def get_requirement_detail_1() -> RequirementDetail:

        requirement_detail_1 : RequirementDetail = RequirementDetail(
            current_package = ObjectMother.get_package_1(),
            most_recent_release = ObjectMother.get_release_1(),
            is_version_matching = True,
            description = "The current version matches the most recent release."
        )

        return requirement_detail_1
    @staticmethod
    def get_requirement_detail_1_as_json() -> str:

        description : str = ObjectMother().get_requirement_detail_1().description
        formatted : str = f"{{ 'description': '{description}' }}"

        return formatted

    @staticmethod
    def get_package_2() -> Package:

        package_2 : Package = Package(name = "opencv-python", version = "4.5.0")

        return package_2
    @staticmethod
    def get_release_2() -> Release:

        release_2 : Release = Release(package_name = "opencv-python", version = "4.10.0", date = datetime(2023, 8, 12))

        return release_2
    @staticmethod
    def get_requirement_detail_2() -> RequirementDetail:

        requirement_detail_2 : RequirementDetail = RequirementDetail(
            current_package = ObjectMother.get_package_2(),
            most_recent_release = ObjectMother.get_release_2(),
            is_version_matching = False,
            description = "The current version ('4.5.0') of 'opencv-python' doesn't match with the most recent release ('4.10.0', '2023-08-12')."
        )

        return requirement_detail_2
    @staticmethod
    def get_requirement_detail_2_as_json() -> str:

        description : str = ObjectMother().get_requirement_detail_2().description
        formatted : str = f"{{ 'description': '{description}' }}"

        return formatted

    @staticmethod
    def get_requirement_details() -> list[RequirementDetail]:

        requirement_details : list[RequirementDetail] = [
            ObjectMother.get_requirement_detail_1(), 
            ObjectMother.get_requirement_detail_2()
        ]

        return requirement_details
    @staticmethod
    def get_requirement_details_as_json() -> str:

        formatted : str = str.join("\n", [
			ObjectMother.get_requirement_detail_1_as_json(),
			ObjectMother.get_requirement_detail_2_as_json()
		])

        return formatted  

    @staticmethod
    def get_requirement_summary() -> RequirementSummary:

        requirement_summary : RequirementSummary = RequirementSummary(
            total_packages = 2,
            matching = 1,
            matching_prc = "50.00%",
            mismatching = 1,
            mismatching_prc = "50.00%",
            details = ObjectMother.get_requirement_details()
        )

        return requirement_summary
    @staticmethod
    def get_requirement_summary_as_json_without_details() -> str:

        formatted : str = "{ 'total_packages': '2', 'matching': '1', 'matching_prc': '50.00%', 'mismatching': '1', 'mismatching_prc': '50.00%' }"

        return formatted
    @staticmethod
    def get_requirement_summary_as_json_with_details() -> str:

        formatted_summary : str = ObjectMother.get_requirement_summary_as_json_without_details()
        formatted_details : str = ObjectMother.get_requirement_details_as_json()
        formatted : str = str.join("\n", [formatted_summary, formatted_details])

        return formatted
class SupportMethodProvider():

    '''Collection of generic purpose test-aiding methods.'''

    @staticmethod
    def __are_lists_equal(list1 : list[Any], list2 : list[Any], comparer : Callable[[Any, Any], bool]) -> bool:

        '''Returns True if all the items of list1 contain the same values of the corresponding items of list2.'''

        if (list1 == None and list2 == None):
            return True

        if (list1 == None or list2 == None):
            return False

        if (len(list1) != len(list2)):
            return False

        for i in range(len(list1)):
            if (comparer(list1[i], list2[i]) == False):
                return False

        return True

    @staticmethod
    def are_packages_equal(p1 : Package, p2 : Package) -> bool:

        '''Returns True if all the fields of the two objects contain the same values.'''

        return (
            p1.name == p2.name and
            p1.version == p2.version
        )
    @staticmethod
    def are_lists_of_packages_equal(list1 : list[Package], list2 : list[Package]) -> bool:

        '''Returns True if all the items of list1 contain the same values of the corresponding items of list2.'''

        return SupportMethodProvider.__are_lists_equal(
                list1 = list1, 
                list2 = list2, 
                comparer = lambda p1,p2 : SupportMethodProvider.are_packages_equal(p1, p2)
            )

    @staticmethod
    def are_releases_equal(r1 : Release, r2 : Release) -> bool:

        '''Returns True if all the fields of the two objects contain the same values.'''

        return (
            r1.package_name == r2.package_name and
            r1.version == r2.version and
            r1.date == r2.date
        )
    @staticmethod
    def are_lists_of_releases_equal(list1 : list[Release], list2 : list[Release]) -> bool:

        '''Returns True if all the items of list1 contain the same values of the corresponding items of list2.'''

        return SupportMethodProvider.__are_lists_equal(
                list1 = list1, 
                list2 = list2, 
                comparer = lambda p1,p2 : SupportMethodProvider.are_releases_equal(p1, p2)
            )

    @staticmethod
    def are_requirementdetails_equal(sd1 : RequirementDetail, sd2 : RequirementDetail) -> bool:

        '''Returns True if all the fields of the two objects contain the same values.'''

        return (
            SupportMethodProvider.are_packages_equal(sd1.current_package, sd2.current_package) and
            SupportMethodProvider.are_releases_equal(sd1.most_recent_release, sd2.most_recent_release) and
            sd1.is_version_matching == sd2.is_version_matching and
            sd1.description == sd2.description
            )
    @staticmethod
    def are_lists_of_requirementdetails_equal(list1 : list[RequirementDetail], list2 : list[RequirementDetail]) -> bool:

        '''Returns True if all the items of list1 contain the same values of the corresponding items of list2.'''

        return SupportMethodProvider.__are_lists_equal(
                list1 = list1, 
                list2 = list2, 
                comparer = lambda sd1, sd2 : SupportMethodProvider.are_requirementdetails_equal(sd1, sd2)
            )

    @staticmethod
    def are_xmlitems_equal(xi1 : XMLItem, sxi2 : XMLItem) -> bool:

        '''Returns True if all the fields of the two objects contain the same values.'''

        return (
            xi1.title == sxi2.title and
            xi1.link == sxi2.link and
            xi1.description == sxi2.description and
            xi1.author == sxi2.author and
            xi1.pubdate == sxi2.pubdate and
            xi1.pubdate_str == sxi2.pubdate_str
            )
    @staticmethod
    def are_lists_of_xmlitems_equal(list1 : list[XMLItem], list2 : list[XMLItem]) -> bool:

        '''Returns True if all the items of list1 contain the same values of the corresponding items of list2.'''

        return SupportMethodProvider.__are_lists_equal(
                list1 = list1, 
                list2 = list2, 
                comparer = lambda xi1, xi2 : SupportMethodProvider.are_xmlitems_equal(xi1, xi2)
            )

    @staticmethod
    def are_badges_equal(b1 : Badge, b2 : Badge) -> bool:

        '''Returns True if all the fields of the two objects contain the same values.'''

        return (
            b1.package_name == b2.package_name and
            b1.version == b2.version and
            b1.label == b2.label
        )
    @staticmethod
    def are_lists_of_badges_equal(list1 : Optional[list[Badge]], list2 : Optional[list[Badge]]) -> bool:

        '''Returns True if all the items of list1 contain the same values of the corresponding items of list2.'''

        if list1 is None and list2 is not None:
            return False
        
        if list1 is not None and list2 is None:
            return False
        
        if list1 is None and list2 is None:
            return True

        return SupportMethodProvider.__are_lists_equal(
                list1 = cast(list[Badge], list1), 
                list2 = cast(list[Badge], list2), 
                comparer = lambda b1, b2 : SupportMethodProvider.are_badges_equal(b1, b2)
            )

    @staticmethod
    def are_lsessions_equal(ls1 : LSession, ls2 : LSession) -> bool:

        '''Returns True if all the fields of the two objects contain the same values.'''

        return (
            SupportMethodProvider.are_lists_of_packages_equal(ls1.packages, ls2.packages) and
            ls1.unparsed_lines == ls2.unparsed_lines
            )
    @staticmethod
    def are_fsessions_equal(fs1 : FSession, fs2 : FSession) -> bool:

        '''Returns True if all the fields of the two objects contain the same values.'''

        return (
            fs1.package_name == fs2.package_name and
            SupportMethodProvider.are_releases_equal(fs1.most_recent_release, fs2.most_recent_release) and
            SupportMethodProvider.are_lists_of_releases_equal(fs1.releases, fs2.releases) and
            SupportMethodProvider.are_lists_of_xmlitems_equal(fs1.xml_items, fs2.xml_items) and 
            SupportMethodProvider.are_lists_of_badges_equal(fs1.badges, fs2.badges)
            )

# TEST CLASSES
class LSessionTestCase(unittest.TestCase):

    def setUp(self):

        self.packages : list[Package] = [
            Package(name = "requests", version = "2.26.0"),
            Package(name = "asyncio", version = "3.4.3"),
            Package(name = "typed-astunparse", version = "2.1.4"),
            Package(name = "opencv-python", version = "4.10.0.84"),
            Package(name = "black", version = "22.12.0")
        ]
        self.unparsed_lines : list[str] = [
            "FROM python:3.12.5-bookworm", 
            "RUN wget https://github.com/jgm/pandoc/releases/download/3.4/pandoc-3.4-1-amd64.deb \\", 
            "    && dpkg -i pandoc-3.4-1-amd64.deb \\", 
            "    && rm -f pandoc-3.4-1-amd64.deb"
        ]
        self.l_session : LSession = LSession(
            packages = self.packages,
            unparsed_lines = self.unparsed_lines
        )        

    def test_lsession_shouldinitializeasexpected_wheninvoked(self):
	
		# Arrange
        # Act
		# Assert
        self.assertTrue(
            SupportMethodProvider.are_lists_of_packages_equal(
                list1 = self.l_session.packages,
                list2 = self.packages
            ))
        self.assertEqual(self.l_session.unparsed_lines, self.unparsed_lines)
    def test_lsession_shouldreturnexpectedstring_wheninvoked(self):
        
		# Arrange
        expected: str = (
                "{ "
                f"'packages': '{len(self.packages)}', "
                f"'unparsed_lines': '{len(self.unparsed_lines)}'"
                " }"                
            )		
		
        # Act
        actual : str = str(self.l_session)

        # Assert
        self.assertEqual(actual, expected)
class BadgeTestCase(unittest.TestCase):
    
    def setUp(self) -> None:

        self.package_name : str = "numpy"
        self.version : str = "2.1.2alpha"
        self.label : Literal["pre-release", "yanked"] = "pre-release"

        self.badge : Badge = Badge(package_name = self.package_name, version = self.version, label = self.label)

    def test_badge_shouldinitializeasexpected_wheninvoked(self) -> None:

        # Arrange
        # Act
        # Assert
        self.assertEqual(self.badge.package_name, self.package_name)
        self.assertEqual(self.badge.version, self.version)
        self.assertEqual(self.badge.label, self.label)
    def test_str_shouldreturnexpectedstring_wheninvoked(self) -> None:

        # Arrange
        expected : str = str(
            "{ "
            f"'package_name': '{self.package_name}', "
            f"'version': '{self.version}', "
            f"'label': '{self.label}'"
            " }"
        )

        # Act
        actual_str : str = str(self.badge)
        actual_repr : str = repr(self.badge)

        # Assert
        self.assertEqual(actual_str, expected)
        self.assertEqual(actual_repr, expected)
class XMLItemTestCase(unittest.TestCase):

    def setUp(self) -> None:

        self.title : Optional[str] = "2.1.2"
        self.link : Optional[str] = "https://pypi.org/project/numpy/2.1.2/"
        self.description : Optional[str] = "Fundamental package for array computing in Python"
        self.author : Optional[str] = "stephen@hotmail.com"
        self.pubdate : Optional[datetime] = datetime(2024, 10, 5, 18, 28, 18)
        self.pubdate_str : Optional[str] = "Sat, 05 Oct 2024 18:28:18 GMT"

        self.xml_item : XMLItem = XMLItem(
            title = self.title,
            link = self.link,
            description = self.description,
            author = self.author,
            pubdate = self.pubdate,
            pubdate_str = self.pubdate_str
        )

    def test_xmlitem_shouldinitializeasexpected_wheninvoked(self) -> None:
        
        # Arrange
        # Act
        # Assert
        self.assertEqual(self.xml_item.title, self.title)
        self.assertEqual(self.xml_item.link, self.link)
        self.assertEqual(self.xml_item.description, self.description)
        self.assertEqual(self.xml_item.author, self.author)
        self.assertEqual(self.xml_item.pubdate, self.pubdate)
        self.assertEqual(self.xml_item.pubdate_str, self.pubdate_str)
    def test_xmlitem_shouldreturnexpectedstring_whenargumentsarenotnone(self):
        
		# Arrange
        expected : str = (
            "{ 'title': '2.1.2', "
            "'link': 'https://pypi.org/project/numpy/2.1.2/', "
            "'description': 'Fundamental package for array computing in Python', "
            "'author': 'stephen@hotmail.com', "
            "'pubdate_str': 'Sat, 05 Oct 2024 18:28:18 GMT' }"
        )
        
        # Act	
        actual_str : str = str(self.xml_item)
        actual_repr : str = repr(self.xml_item)
        
        # Assert
        self.assertEqual(actual_str, expected)
        self.assertEqual(actual_repr, expected)
    def test_xmlitem_shouldreturnexpectedstring_whenargumentsarenone(self):
        
		# Arrange
        expected : str = (
            "{ 'title': 'None', "
            "'link': 'None', "
            "'description': 'None', "
            "'author': 'None', "
            "'pubdate_str': 'None' }"
        )
        
        # Act
        xml_item : XMLItem = XMLItem(
            title = None,
            link = None,
            description = None,
            author = None,
            pubdate = None,
            pubdate_str = None
        )		
        actual_str : str = str(xml_item)
        actual_repr : str = repr(xml_item)
        
        # Assert
        self.assertEqual(actual_str, expected)
        self.assertEqual(actual_repr, expected)
class ReleaseTestCase(unittest.TestCase):

    def setUp(self) -> None:
	
        self.package_name : str = "numpy"
        self.version : str = "2.1.2"
        self.date : datetime = datetime(2024, 10, 5, 18, 28, 18)

        self.release : Release = Release(
			package_name = self.package_name, 
			version = self.version, 
			date = self.date
		)

    def test_release_shouldinitializeasexpected_wheninvoked(self) -> None:
        
		# Arrange       
        # Act      
        # Assert
        self.assertEqual(self.release.package_name, self.package_name)
        self.assertEqual(self.release.version, self.version)
        self.assertEqual(self.release.date, self.date)
    def test_release_shouldreturnexpectedstring_wheninvoked(self) -> None:
        
		# Arrange
        expected : str = "{ 'package_name': 'numpy', 'version': '2.1.2', 'date': '2024-10-05' }"
        
        # Act		
        actual_str : str = str(self.release)
        actual_repr : str = repr(self.release)
        
        # Assert
        self.assertEqual(actual_str, expected)
        self.assertEqual(actual_repr, expected)
class FSessionTestCase(unittest.TestCase):

    def setUp(self):

        self.package_name : str = "numpy"

        self.releases: list[Release] = [
            Release(package_name="numpy", version="2.1.2", date=datetime.strptime("2024-10-05", "%Y-%m-%d")),
            Release(package_name="numpy", version="2.1.1", date=datetime.strptime("2024-09-03", "%Y-%m-%d")),
            Release(package_name="numpy", version="2.0.2", date=datetime.strptime("2024-08-26", "%Y-%m-%d")),
            Release(package_name="numpy", version="2.1.0", date=datetime.strptime("2024-08-18", "%Y-%m-%d"))
        ]

        self.most_recent_release : Release = Release(
            package_name = "numpy",
            version = "2.1.2",
            date = datetime(2024, 10, 5, 18, 28, 18)
        )

        self.mrr_formatter : Callable[[Release], str] = lambda mrr : f"('{mrr.version}', '{mrr.date.strftime("%Y-%m-%d")}')"
        self.badge_formatter : Callable[[Optional[list[Badge]]], str] = lambda badges : str(None) if badges is None else str(len(badges))

        self.xml_items: list[XMLItem] = [
            XMLItem(title="2.1.2", link="https://pypi.org/project/numpy/2.1.2/", description="Fundamental package for array computing in Python", author=None, pubdate=datetime.strptime("Sat, 05 Oct 2024 18:28:18 GMT", "%a, %d %b %Y %H:%M:%S %Z"), pubdate_str="Sat, 05 Oct 2024 18:28:18 GMT"),
            XMLItem(title="2.1.1", link="https://pypi.org/project/numpy/2.1.1/", description="Fundamental package for array computing in Python", author=None, pubdate=datetime.strptime("Tue, 03 Sep 2024 15:01:06 GMT", "%a, %d %b %Y %H:%M:%S %Z"), pubdate_str="Tue, 03 Sep 2024 15:01:06 GMT"),
            XMLItem(title="2.0.2", link="https://pypi.org/project/numpy/2.0.2/", description="Fundamental package for array computing in Python", author=None, pubdate=datetime.strptime("Mon, 26 Aug 2024 20:04:14 GMT", "%a, %d %b %Y %H:%M:%S %Z"), pubdate_str="Mon, 26 Aug 2024 20:04:14 GMT"),
            XMLItem(title="2.1.0", link="https://pypi.org/project/numpy/2.1.0/", description="Fundamental package for array computing in Python", author=None, pubdate=datetime.strptime("Sun, 18 Aug 2024 21:39:07 GMT", "%a, %d %b %Y %H:%M:%S %Z"), pubdate_str="Sun, 18 Aug 2024 21:39:07 GMT")
        ]

        self.badges : list[Badge] = [
            Badge(package_name = "numpy", version = "2.1.2alpha", label = "pre-release"),
            Badge(package_name = "numpy", version = "2.0.2d0", label = "yanked")
        ]

        self.f_session : FSession = FSession(
            package_name = self.package_name,
            most_recent_release = self.most_recent_release,
            releases = self.releases,
            xml_items = self.xml_items,
            badges = self.badges
        )

    def test_fsession_shouldinitializeasexpected_wheninvoked(self):
	
		# Arrange
        # Act	
		# Assert
        self.assertEqual(self.f_session.package_name, self.package_name)
        self.assertEqual(self.f_session.most_recent_release.package_name, self.most_recent_release.package_name)
        self.assertEqual(self.f_session.most_recent_release.version, self.most_recent_release.version)
        self.assertEqual(self.f_session.most_recent_release.date, self.most_recent_release.date)
        self.assertEqual(self.f_session.releases, self.releases)
        self.assertEqual(self.f_session.xml_items, self.xml_items)
        self.assertEqual(self.f_session.badges, self.badges)
    def test_fsession_shouldreturnexpectedstring_whenbadgesisnotnone(self):
        
		# Arrange
        expected: str = (
            "{ 'package_name': 'numpy', "
            f"'most_recent_release': '{self.mrr_formatter(self.most_recent_release)}', "
            "'releases': '4', "
            "'xml_items': '4', "
            f"'badges': '{self.badge_formatter(self.badges)}' "
            "}"
        )
		
        # Act
        actual : str = str(self.f_session)

        # Assert
        self.assertEqual(actual, expected)
    def test_fsession_shouldreturnexpectedstring_whenbadgesisnone(self):
        
		# Arrange
        expected: str = (
            "{ 'package_name': 'numpy', "
            f"'most_recent_release': '{self.mrr_formatter(self.most_recent_release)}', "
            "'releases': '4', "
            "'xml_items': '4', "
            "'badges': 'None' "
            "}"
        )
		
        # Act
        f_session : FSession = FSession(
            package_name = self.package_name,
            most_recent_release = self.most_recent_release,
            releases = self.releases,
            xml_items = self.xml_items,
            badges = None
        )
        actual : str = str(f_session)

        # Assert
        self.assertEqual(actual, expected)
class LambdaCollectionTestCase(unittest.TestCase):

    def test_getfunction_shouldreturnexpectedstatuscodeandtext_wheninvoked(self):
	
        # Arrange
        expected_sc : int = 200
        expected_text : str = '<rss version="2.0"></rss>'
        response_mock : MagicMock = MagicMock(spec = Response)
        response_mock.status_code = expected_sc
        response_mock.text = expected_text
        url : str = "https://pypi.org/rss/project/numpy/releases.xml"

		# Act
        actual : Optional[Response] = None
        with patch("requests.get", return_value = response_mock):
            get_function : Callable[[str], Response] = LambdaCollection.get_function()
            actual = get_function(url)

        # Assert
        self.assertEqual(cast(Response, actual).status_code, expected_sc)
        self.assertEqual(cast(Response, actual).text, expected_text)
    def test_loggingfunction_shouldbecalledwithexpectedmessage_wheninvoked(self):
        
        # Arrange
        msg : str = "Some message"

        # Act
        with patch("builtins.print") as print_mock:
            logging_function: Callable[[str], None] = LambdaCollection.logging_function()
            logging_function(msg)

        # Assert
        print_mock.assert_called_once_with(msg)
    def test_filereaderfunction_shouldbecalledwithexpectedargumentsandreturnexpectedcontent_wheninvoked(self):
        
        # Arrange
        expected : str = "requests==2.31.0"
        open_mock = mock_open(read_data = expected)
        file_path : str = "C:/requirements.txt"

        # Act
        actual : Optional[str] = None
        with patch("builtins.open", open_mock):
            file_reader_function : Callable[[str], str] = LambdaCollection.file_reader_function()
            actual = file_reader_function(file_path)

        # Assert
        open_mock.assert_called_once_with(file_path, "r", encoding = "utf-8")
        self.assertEqual(str(actual), expected)
    def test_sleepingfunction_shoulddelayexecutionbywaitingtime_wheninvoked(self):
	
        # Arrange
        waiting_time : int = 2
        sleeping_function : Callable[[int], None] = LambdaCollection.sleeping_function()
        
        # Act
        start_time : float = time()
        sleeping_function(waiting_time)
        end_time : float = time()
        
        # Assert
        elapsed_time : float = end_time - start_time
        self.assertAlmostEqual(elapsed_time, waiting_time, delta=0.1)
    def test_donothingfunction_shoulddonothing_wheninvoked(self) -> None:
        
        # Arrange
        do_nothing_function : Callable[[Any], None] = LambdaCollection.do_nothing_function()

        # Act, Assert
        do_nothing_function("test")
class ValidatorTestCase(unittest.TestCase):

    def test_validatewaitingtime_shouldraiseexceptionwithexpectedmessage_whenwaitingtimelessthanminimum(self):

        # Arrange
        waiting_time : int = 2
        minimum_wt : int = 5
        expected : str = _MessageCollection.waiting_time_cant_be_less_than(waiting_time, minimum_wt)

        # Act, Assert
        with self.assertRaises(Exception) as context:
            Validator.validate_waiting_time(waiting_time = waiting_time)
        
        self.assertEqual(str(context.exception), expected)
    def test_validatewaitingtime_shoulddonothing_whenwaitingtimeisgreaterthanorequaltominimum(self):

        # Arrange
        waiting_time : int = 5

        # Act, Assert
        Validator.validate_waiting_time(waiting_time = waiting_time)

    def test_validatefilepath_shouldraiseexceptionwithexpectedmessage_whenfiledoesnotexist(self):

        # Arrange
        file_path : str = r"C:/NonExistentFile.txt"
        expected : str = _MessageCollection.provided_file_path_doesnt_exist(file_path)

        # Act, Assert
        with patch("os.path.isfile", return_value = False):
            with self.assertRaises(Exception) as context:
                Validator.validate_file_path(file_path = file_path)
            
            self.assertEqual(str(context.exception), expected)
    def test_validatefilepath_shoulddonothing_whenfileexists(self):

        # Arrange
        file_path : str = r"C:/Exists.txt"

        # Act, Assert
        with patch("os.path.isfile", return_value = True):
            Validator.validate_file_path(file_path = file_path)
class JsonFormatterTestCase(unittest.TestCase):

    def test_formatrequirementdetail_shouldreturnexpectedstring_wheninvoked(self):

        # Arrange
        requirement_detail : RequirementDetail = ObjectMother.get_requirement_detail_2()
        expected : str = ObjectMother.get_requirement_detail_2_as_json()

        # Act
        actual : str = JsonFormatter().format_requirement_detail(requirement_detail)

        # Assert
        self.assertEqual(actual, expected)
    def test_formatrequirementdetails_shouldreturnexpectedstring_wheninvoked(self):

        # Arrange
        requirement_details : list[RequirementDetail] = ObjectMother.get_requirement_details()
        expected : str = ObjectMother.get_requirement_details_as_json()

        # Act
        actual : str = JsonFormatter().format_requirement_details(requirement_details)

        # Assert
        self.assertEqual(actual, expected)
    def test_formatrequirementsummary_shouldreturnexpectedstring_whenwithdetailsisfalse(self):

        # Arrange
        requirement_summary : RequirementSummary = ObjectMother.get_requirement_summary()
        expected : str = ObjectMother.get_requirement_summary_as_json_without_details()

        # Act
        actual : str = JsonFormatter().format_requirement_summary(requirement_summary, with_details = False)

        # Assert
        self.assertEqual(actual, expected)
    def test_formatrequirementsummary_shouldreturnexpectedstring_whenwithdetailsistrue(self):

        # Arrange
        requirement_summary : RequirementSummary = ObjectMother.get_requirement_summary()
        expected : str = ObjectMother.get_requirement_summary_as_json_with_details()

        # Act
        actual : str = JsonFormatter().format_requirement_summary(requirement_summary, with_details = True)

        # Assert
        self.assertEqual(actual, expected)
class BasicFormatterTestCase(unittest.TestCase):

    def test_formatrequirementdetail_shouldreturnexpectedstring_wheninvoked(self):

        # Arrange
        requirement_detail : RequirementDetail = ObjectMother.get_requirement_detail_2()
        expected : str = requirement_detail.description

        # Act
        actual : str = BasicFormatter().format_requirement_detail(requirement_detail)

        # Assert
        self.assertEqual(actual, expected)
    def test_formatrequirementdetails_shouldreturnexpectedstring_wheninvoked(self):

        # Arrange
        requirement_details : list[RequirementDetail] = ObjectMother.get_requirement_details()
        expected : str = str.join("\n", [detail.description for detail in requirement_details])

        # Act
        actual : str = BasicFormatter().format_requirement_details(requirement_details)

        # Assert
        self.assertEqual(actual, expected)
    def test_formatrequirementsummary_shouldreturnexpectedstring_whenwithdetailsisfalse(self):

        # Arrange
        requirement_summary : RequirementSummary = ObjectMother.get_requirement_summary()
        expected_lines : list[str] = [
            f"total_packages: '{str(requirement_summary.total_packages)}'",
            f"matching: '{str(requirement_summary.matching)}'",
            f"matching_prc: '{requirement_summary.matching_prc}'",
            f"mismatching: '{str(requirement_summary.mismatching)}'",
            f"mismatching_prc: '{requirement_summary.mismatching_prc}'"
        ]
        expected : str = str.join("\n", expected_lines)

        # Act
        actual : str = BasicFormatter().format_requirement_summary(requirement_summary, with_details = False)

        # Assert
        self.assertEqual(actual, expected)
    def test_formatrequirementsummary_shouldreturnexpectedstring_whenwithdetailsistrue(self):

        # Arrange
        requirement_summary : RequirementSummary = ObjectMother.get_requirement_summary()
        formatter : BasicFormatter = BasicFormatter()
        
        summary_lines : list[str] = [
            f"total_packages: '{str(requirement_summary.total_packages)}'",
            f"matching: '{str(requirement_summary.matching)}'",
            f"matching_prc: '{requirement_summary.matching_prc}'",
            f"mismatching: '{str(requirement_summary.mismatching)}'",
            f"mismatching_prc: '{requirement_summary.mismatching_prc}'"
        ]
        details : str = formatter.format_requirement_details(requirement_summary.details)
        expected : str = str.join("\n", [str.join("\n", summary_lines), "", details])

        # Act
        actual : str = formatter.format_requirement_summary(requirement_summary, with_details = True)

        # Assert
        self.assertEqual(actual, expected)
class LocalPackageLoaderTestCase(unittest.TestCase):

    def setUp(self) -> None:

        self.file_reader_function : Callable[[str], str] = LambdaCollection.file_reader_function()
        self.file_reader_mock: Callable[[str], str] = Mock(return_value = "content")

    def test_localpackageloader_shouldinitializeasexpected_wheninvoked(self) -> None:
        
        # Arrange
        # Act
        package_loader : LocalPackageLoader = LocalPackageLoader(file_reader_function = self.file_reader_function)

        # Assert
        self.assertIsInstance(package_loader, LocalPackageLoader)
    def test_cleanunparsedlines_shouldremovermptystrings_whenlinesprovided(self) -> None:
        
        # Arrange
        unparsed_lines : list[str] = ["line1", "", "line2", ""]
        expected : list[str] = ["line1", "line2"]

        # Act
        package_loader : LocalPackageLoader = LocalPackageLoader(file_reader_function = self.file_reader_mock)
        actual : list[str] = package_loader._LocalPackageLoader__clean_unparsed_lines(unparsed_lines = unparsed_lines) # type: ignore

        # Assert
        self.assertEqual(actual, expected)
    
    @parameterized.expand([
        [r"C:/requirements.txt", True],
        [r"C:/requirements_175621.txt", True],
        [r"C:/requirements_demo.txt", True],
        [r"C:/some_file_name.txt", False]
    ])
    def test_isrequirements_shouldreturnexpectedbool_wheninvoked(self, file_path : str, expected : bool) -> None:
        
        # Arrange
        # Act
        package_loader : LocalPackageLoader = LocalPackageLoader(file_reader_function = self.file_reader_mock)
        actual : bool = package_loader._LocalPackageLoader__is_requirements(file_path) # type: ignore

        # Assert
        self.assertEqual(actual, expected)

    @parameterized.expand([
        [r"C:/Dockerfile", True],
        [r"C:/Dockerfile_175621", True],
        [r"C:/Dockerfile_demo", True],
        [r"C:/some_file_name", False]
    ])
    def test_isdockerfile_shouldreturnexpectedbool_wheninvoked(self, file_path : str, expected : bool) -> None:
        
        # Arrange
        # Act
        package_loader : LocalPackageLoader = LocalPackageLoader(file_reader_function = self.file_reader_mock)
        actual : bool = package_loader._LocalPackageLoader__is_dockerfile(file_path) # type: ignore

        # Assert
        self.assertEqual(actual, expected)

    def test_load_shouldreturnexpectedlsession_whenrequirements(self) -> None:
        
        # Arrange
        file_path : str = "requirements.txt"
        file_content: str = "\n".join([
            "requests >= 2.26.0", 
            "asyncio == 3.4.3", 
            "Some unparsable line.", 
            ""
        ])
        file_reader_mock : Callable[[str], str] = Mock(return_value = file_content)
        expected : LSession = LSession(
            packages = [
                Package(name = "requests", version = "2.26.0"),
                Package(name = "asyncio", version = "3.4.3")
            ],
            unparsed_lines = ["Some unparsable line."]

        )

        # Act
        package_loader : LocalPackageLoader = LocalPackageLoader(file_reader_function = file_reader_mock)
        actual : LSession = package_loader.load(file_path = file_path)

        # Assert
        self.assertTrue(
            SupportMethodProvider.are_lsessions_equal(
                ls1 = actual,
                ls2 = expected
            ))
    def test_load_shouldreturnexpectedlsession_whendockerfile(self) -> None:
        
        # Arrange
        file_path : str = "Dockerfile"
        file_content: str = "\n".join([
            "FROM python:3.12.5-bookworm", 
            "RUN pip install requests==2.26.0", 
            "RUN pip install beautifulsoup4==4.10.0", 
            ""
        ])
        file_reader_mock : Callable[[str], str] = Mock(return_value = file_content)
        expected : LSession = LSession(
            packages = [
                Package(name = "requests", version = "2.26.0"),
                Package(name = "beautifulsoup4", version = "4.10.0")
            ],
            unparsed_lines = ["FROM python:3.12.5-bookworm"]

        )

        # Act
        package_loader : LocalPackageLoader = LocalPackageLoader(file_reader_function = file_reader_mock)
        actual : LSession = package_loader.load(file_path = file_path)

        # Assert
        self.assertTrue(
            SupportMethodProvider.are_lsessions_equal(
                ls1 = actual,
                ls2 = expected
            ))
    
    @parameterized.expand([
        [r"C:/randomfile.txt", _MessageCollection.no_loading_strategy_found(r"C:/randomfile.txt")],
        [r"C:/Dockerfile", _MessageCollection.no_packages_found(r"C:/Dockerfile")]
    ])    
    def test_load_shouldraiseexceptionandexpectedmessage_whenunexpected(self, file_path : str, msg : str) -> None:
        
        # Arrange
        # Act, Assert
        with self.assertRaises(expected_exception = Exception, msg = msg):
            package_loader : LocalPackageLoader = LocalPackageLoader(file_reader_function = self.file_reader_mock)
            package_loader.load(file_path = file_path)
class PyPiBadgeFetcherTestCase(unittest.TestCase):

    def setUp(self) -> None:

        self.badge_fetcher : PyPiBadgeFetcher = PyPiBadgeFetcher()
    
        self.html_response : str = str(
            '<div class="release-timeline">'
            '<div class="release release--latest">'
            '<div class="release__meta"></div>'
            '<div class="release__graphic">'
            '<div class="release__line"></div>'
            '<img class="release__node" alt="" src="https://pypi.org/static/images/white-cube.2351a86c.svg">'
            '</div>'
            '<a class="card release__card" href="/project/ipykernel/7.0.0a0/">'
            '<p class="release__version">7.0.0a0'
            '<span class="badge badge--warning">pre-release</span>'
            '</p>'
            '<p class="release__version-date">'
            '<time datetime="2024-10-22T08:26:22+0000">Oct 22, 2024</time>'
            '</p>'
            '</a>'
            '</div>'
            '<div class="release release--current">'
            '<div class="release__meta"><span class="badge">This version</span></div>'
            '<div class="release__graphic">'
            '<div class="release__line"></div>'
            '<img class="release__node" alt="" src="https://pypi.org/static/images/blue-cube.572a5bfb.svg">'
            '</div>'
            '<a class="card release__card" href="/project/ipykernel/6.29.5/">'
            '<p class="release__version">6.29.5</p>'
            '<p class="release__version-date">'
            '<time datetime="2024-07-01T14:07:19+0000">Jul 1, 2024</time>'
            '</p>'
            '</a>'
            '</div>'
            '<div class="release">'
            '<div class="release__meta"></div>'
            '<div class="release__graphic">'
            '<div class="release__line"></div>'
            '<img class="release__node" alt="" src="https://pypi.org/static/images/white-cube.2351a86c.svg">'
            '</div>'
            '<a class="card release__card" href="/project/ipykernel/6.29.4/">'
            '<p class="release__version">6.29.4</p>'
            '<p class="release__version-date">'
            '<time datetime="2024-03-27T22:25:41+0000">Mar 27, 2024</time>'
            '</p>'
            '</a>'
            '</div>'
            '<div class="release__graphic">'
            '<div class="release__line"></div>'
            '<img class="release__node" alt="" src="https://pypi.org/static/images/white-cube.2351a86c.svg">'
            '</div>'
            '<a class="card release__card" href="/project/ipykernel/6.27.0/">'
            '<p class="release__version">6.27.0'
            '<span class="badge badge--danger">yanked</span>'
            '</p>'
            '<p class="release__version-date">'
            '<time datetime="2023-11-21T11:23:46+0000">Nov 21, 2023</time>'
            '</p>'
            '<div class="callout-block callout-block--danger release__yanked-reason">'
            '<p>Reason this release was yanked:</p><p>broke %edit magic</p>'
            '</div>'
            '</a>'
            '</div>'
        ) 
        self.package_name : str = "ipykernel"
        self.badges : list[Badge] = [
            Badge(package_name = "ipykernel", version = "7.0.0a0", label = "pre-release"),
            Badge(package_name = "ipykernel", version = "6.27.0", label = "yanked")
        ]

        self.response_mock : Response = Mock(content = self.html_response)       
        self.get_function_mock : Callable[[str], Response] = Mock(return_value = self.response_mock)

    def test_pypibadgefetcher_shouldinitializeasexpected_wheninvoked(self) -> None:
        
        # Arrange
        # Act
        # Assert
        self.assertIsInstance(self.badge_fetcher, PyPiBadgeFetcher)
        self.assertTrue(callable(self.badge_fetcher._PyPiBadgeFetcher__get_function))   # type: ignore
    def test_formaturl_shouldreturnexpectedurl_wheninvoked(self) -> None:

        # Arrange
        package_name : str = "pandas"
        expected : str = "https://pypi.org/project/pandas/#history"
        
        # Act
        actual : str = self.badge_fetcher._PyPiBadgeFetcher__format_url(package_name = package_name)  # type: ignore
        
        # Assert
        self.assertEqual(actual, expected)
    def test_tryfetch_shouldreturnexpectedbadges_wheninvoked(self) -> None:
        
        # Arrange       
        # Act
        badge_fetcher = PyPiBadgeFetcher(get_function = self.get_function_mock)
        actual : Optional[list[Badge]] = badge_fetcher.try_fetch(package_name = self.package_name)
        
        # Assert
        self.assertTrue(SupportMethodProvider().are_lists_of_badges_equal(list1 = actual, list2 = self.badges))
    def test_tryfetch_shouldreturnnone_whennobadgesfound(self) -> None:
        
        # Arrange
        response_mock : Response = Mock(content = "<html></html>")
        get_function_mock : Callable[[str], Response] = Mock(return_value = response_mock)
        package_name : str = "non_existent_package"       
        
        # Act
        badge_fetcher = PyPiBadgeFetcher(get_function = get_function_mock)
        actual : Optional[list[Badge]] = badge_fetcher.try_fetch(package_name = package_name)
        
        # Assert
        self.assertIsNone(actual)
class PyPiReleaseFetcherTestCase(unittest.TestCase):

    def setUp(self) -> None:

        self.xml_content : str = '\n'.join([
			'<?xml version="1.0" encoding="UTF-8"?>',
			'<rss version="2.0">',
			'  <channel>',
			'    <item>',
			'      <title>2.2.3</title>',
			'      <link>https://pypi.org/project/pandas/2.2.3/</link>',
			'      <description>Powerful data structures for data analysis, time series, and statistics</description>',
			'      <author>pandas-dev@python.org</author>',
			'      <pubDate>Fri, 20 Sep 2024 13:08:42 GMT</pubDate>',
			'    </item>',
			'    <item>',
			'      <title>2.2.2</title>',
			'      <link>https://pypi.org/project/pandas/2.2.2/</link>',
			'      <description>Powerful data structures for data analysis, time series, and statistics</description>',
			'      <author>pandas-dev@python.org</author>',
			'      <pubDate>Wed, 10 Apr 2024 19:44:10 GMT</pubDate>',
			'    </item>',
			'  </channel>',
			'</rss>'
		])
        
        self.xml_response : Response = Mock()
        self.xml_response.text = self.xml_content
        self.get_function_mock : Callable[[str], Response] = Mock(return_value = self.xml_response)

        self.xml_items : list[XMLItem] = [
            XMLItem(
                title = "2.2.3", 
                link = "https://pypi.org/project/pandas/2.2.3/", 
                description = "Powerful data structures for data analysis, time series, and statistics",
                author = "pandas-dev@python.org",
                pubdate = datetime(2024, 9, 20, 13, 8, 42),
                pubdate_str = "Fri, 20 Sep 2024 13:08:42 GMT"
                ),
            XMLItem(
                title = "2.2.2", 
                link = "https://pypi.org/project/pandas/2.2.2/", 
                description = "Powerful data structures for data analysis, time series, and statistics",
                author = "pandas-dev@python.org",
                pubdate = datetime(2024, 4, 10, 19, 44, 10),
                pubdate_str = "Wed, 10 Apr 2024 19:44:10 GMT"
                ),
        ]
        self.releases : list[Release] = [
            Release(package_name = "pandas", version = "2.2.3", date = datetime(2024, 9, 20, 13, 8, 42)),
            Release(package_name = "pandas", version = "2.2.2", date = datetime(2024, 4, 10, 19, 44, 10))
        ]

        self.badges : list[Badge] = [
            Badge(package_name = "numpy", version = "2.2.3alpha", label = "pre-release"),
            Badge(package_name = "numpy", version = "2.2.2d0", label = "yanked")
        ]
    
        self.badge_fetcher_mock : PyPiBadgeFetcher = Mock()
        self.badge_fetcher_mock.try_fetch.return_value = self.badges

    def test_pypireleasefetcher_shouldinitializeasexpected_wheninvoked(self) -> None:
        
        # Arrange
        # Act
        release_fetcher : PyPiReleaseFetcher = PyPiReleaseFetcher()

        # Assert
        self.assertIsInstance(release_fetcher, PyPiReleaseFetcher)
        self.assertTrue(callable(release_fetcher._PyPiReleaseFetcher__get_function))                    # type: ignore
        self.assertIsInstance(release_fetcher._PyPiReleaseFetcher__badge_fetcher, PyPiBadgeFetcher)     # type: ignore
    def test_fetch_shouldraiseexception_whenxmlitemsarezero(self) -> None:
        
        # Arrange
        xml_content : str = self.xml_content.replace("<title>2.2.3</title>", "<title></title>")
        xml_content = xml_content.replace("<pubDate>Wed, 10 Apr 2024 19:44:10 GMT</pubDate>", "")       
        xml_response : Mock = Mock(spec = Response)
        xml_response.text = xml_content

        get_function_mock : Callable[[str], Response] = Mock(return_value = xml_response)
        msg : str = _MessageCollection.no_suitable_xml_items_found(url = "https://pypi.org/rss/project/pandas/releases.xml")

        # Act, Assert
        with self.assertRaises(expected_exception = Exception, msg = msg):
            release_fetcher : PyPiReleaseFetcher = PyPiReleaseFetcher(get_function = get_function_mock)
            release_fetcher.fetch(package_name = "pandas", only_stable_releases = False)
    def test_fetch_shouldreturnexpectedfsession_whenonlystablereleasesisfalse(self) -> None:
        
        # Arrange
        expected : FSession = FSession(
            package_name = "pandas",
            most_recent_release = self.releases[0],
            releases = self.releases,
            xml_items = self.xml_items,
            badges = None
        )
        
        # Act
        release_fetcher : PyPiReleaseFetcher = PyPiReleaseFetcher(get_function = self.get_function_mock)
        actual : FSession = release_fetcher.fetch(package_name = "pandas", only_stable_releases = False)

        # Assert
        self.assertEqual(actual, expected)
    def test_fetch_shouldreturnexpectedfsession_whenonlystablereleasesistrue(self) -> None:
        
        # Arrange
        expected : FSession = FSession(
            package_name = "pandas",
            most_recent_release = self.releases[0],
            releases = self.releases,
            xml_items = self.xml_items,
            badges = self.badges
        )
        
        # Act
        release_fetcher : PyPiReleaseFetcher = PyPiReleaseFetcher(get_function = self.get_function_mock, badge_fetcher = self.badge_fetcher_mock)
        actual : FSession = release_fetcher.fetch(package_name = "pandas", only_stable_releases = True)

        # Assert
        self.assertEqual(actual, expected)
    def test_fetch_shouldreturnexpectedfsession_whenonlystablereleasesistrueandtrycatchreturnsnone(self) -> None:
        
        # Arrange
        badge_fetcher_mock : PyPiBadgeFetcher = Mock()
        badge_fetcher_mock.try_fetch.return_value = None

        expected : FSession = FSession(
            package_name = "pandas",
            most_recent_release = self.releases[0],
            releases = self.releases,
            xml_items = self.xml_items,
            badges = None
        )        
        
        # Act
        release_fetcher : PyPiReleaseFetcher = PyPiReleaseFetcher(get_function = self.get_function_mock, badge_fetcher = badge_fetcher_mock)
        actual : FSession = release_fetcher.fetch(package_name = "pandas", only_stable_releases = True)

        # Assert
        self.assertEqual(actual, expected)

    @parameterized.expand([
        ["Fri, 20 Sep 2024 13:08:42 GMT", datetime(2024, 9, 20, 13, 8, 42)],
        [None, None]
    ])
    def test_parsepubdatestr_shouldreturndatetimeornone_wheninvoked(self, pubdate_str : Optional[str], expected : Optional[datetime]) -> None:
        
        # Arrange      
        # Act
        release_fetcher : PyPiReleaseFetcher = PyPiReleaseFetcher(get_function = self.get_function_mock)
        actual : Optional[datetime] = release_fetcher._PyPiReleaseFetcher__parse_pubdate_str(pubdate_str) # type: ignore

        # Assert
        self.assertEqual(actual, expected)
class RuntimeCheckerTestCase(unittest.TestCase):

    def test_getruntimeversion_shouldreturnexpectedtuple_wheninvoked(self):

        # Arrange
        expected : Tuple[int, int, int] = (3, 12, 5)
        stdout : str = "Python 3.12.5\n"
        process : MagicMock = MagicMock(spec = subprocess.CompletedProcess)
        process.stdout = stdout
        
        # Act
        runtime_checker : RuntimeChecker = RuntimeChecker()
        actual : Optional[Tuple[int, int, int]] = None

        with patch("platform.system", return_value = "Linux"):
            with patch("subprocess.run", return_value = process) as run:
                actual = runtime_checker._RuntimeChecker__get_runtime_version() #type: ignore

        # Assert
        run.assert_called_once_with(["python3", "--version"], capture_output = True, text = True, check = True)
        self.assertEqual(actual, expected)
    def test_getruntimeversion_shouldraiseexception_whenoutputisunexpected(self):

        # Arrange
        stdout : str = "Invalid Output"
        process : MagicMock = MagicMock(spec = subprocess.CompletedProcess)
        process.stdout = stdout

        # Act, Assert
        runtime_checker : RuntimeChecker = RuntimeChecker()

        with patch("subprocess.run", return_value = process):
            with self.assertRaises(Exception) as context:
                runtime_checker._RuntimeChecker__get_runtime_version() #type: ignore

            self.assertEqual(
                _MessageCollection.python_version_unexpected_output(),
                str(context.exception))

    @parameterized.expand([
        [(3, 12, 1), (3, 12, 1), "The installed Python version is matching the expected one (installed: '3.12.1', expected: '3.12.1')."],
        [(3, 11, 11), (3, 12, 1), "Warning! The installed Python is not matching the expected one (installed: '3.11.11', expected: '3.12.1')."],
    ])
    def test_getstatus_shouldreturnexpectedstring_wheninvoked(self, installed : Tuple[int, int, int], required : Tuple[int, int, int], expected : str):

        # Arrange
        with patch.object(RuntimeChecker, "_RuntimeChecker__get_runtime_version", return_value = installed):

            # Act
            actual : str = RuntimeChecker().get_status(required = required)

            # Assert
            self.assertEqual(actual, expected)

    def test_trygetstatus_shouldreturnexpectedstatus_whennoexceptionisraised(self):

        # Arrange
        installed : Tuple[int, int, int] = (3, 12, 1)
        required : Tuple[int, int, int] = (3, 12, 1)
        expected : str = "The installed Python version is matching the expected one (installed: '3.12.1', expected: '3.12.1')."
        
        with patch.object(RuntimeChecker, "_RuntimeChecker__get_runtime_version", return_value = installed):

            # Act
            actual : str = RuntimeChecker().try_get_status(required = required)

            # Assert
            self.assertEqual(actual, expected)
    def test_trygetstatus_shouldreturnexceptionmessage_whenexceptionisraised(self):

        # Arrange
        expected : str = "Some error occurred."
        required : Tuple[int, int, int] = (3, 12, 1)
        
        with patch.object(RuntimeChecker, "_RuntimeChecker__get_runtime_version", side_effect = Exception(expected)):

            # Act
            actual : str = RuntimeChecker().try_get_status(required = required)

            # Assert
            self.assertEqual(actual, expected)
class RequirementCheckerTestCase(unittest.TestCase):

    def setUp(self) -> None:

        self.package1 : Package = Package(name = "pandas", version = "2.2.3")
        self.release1 : Release = Release(package_name = "pandas", version = "2.2.3", date = datetime(2024, 9, 20, 13, 8, 42))
        self.expected_tpl1 : Tuple[bool, str] = (True, _MessageCollection.current_version_matches(self.package1, self.release1))

        self.l_session1 : LSession = LSession(
            packages = [ self.package1 ],
            unparsed_lines = []
        )

        self.f_session1 : FSession = FSession(
            package_name = "pandas",
            most_recent_release = self.release1,
            releases = [self.release1],
            xml_items = [
                XMLItem(title="2.1.2", link="https://pypi.org/project/pandas/2.2.3/", description="", author=None, pubdate=datetime.strptime("Sat, 05 Oct 2024 18:28:18 GMT", "%a, %d %b %Y %H:%M:%S %Z"), pubdate_str="Sat, 05 Oct 2024 18:28:18 GMT"),
            ],
            badges = None
        )

        self.requirement_detail1 : RequirementDetail = RequirementDetail(
            current_package = self.package1,
            most_recent_release = self.release1,
            is_version_matching = self.expected_tpl1[0],
            description = self.expected_tpl1[1]
        )
        self.expected_sd1 : list[RequirementDetail] = [ self.requirement_detail1 ]

        self.package2 : Package = Package(name = "pandas", version = "2.2.2")
        self.release2 : Release = Release(package_name = "pandas", version = "2.2.3", date = datetime(2024, 9, 20, 13, 8, 42))
        self.expected_tpl2 : Tuple[bool, str] = (False, _MessageCollection.current_version_doesnt_match(self.package2, self.release2))

    def test_compare_shouldreturnexpectedtuple_whenversionsmatch(self) -> None:
        
        # Arrange
        # Act
        requirement_checker : RequirementChecker = RequirementChecker()
        actual : Tuple[bool, str] = requirement_checker._RequirementChecker__compare(current_package = self.package1, most_recent_release = self.release1) # type: ignore
        
        # Assert
        self.assertEqual(actual, self.expected_tpl1)
    def test_compare_shouldreturnexpectedtuple_whenversionsmismatch(self) -> None:
        
        # Arrange
        # Act
        requirement_checker : RequirementChecker = RequirementChecker()
        actual : Tuple[bool, str] = requirement_checker._RequirementChecker__compare(current_package = self.package2, most_recent_release = self.release2) # type: ignore
        
        # Assert
        self.assertEqual(actual, self.expected_tpl2)
    def test_createrequirementdetails_shouldreturnexpectedlistofrequirementdetails_wheninvoked(self) -> None:
        
        # Arrange
        # Act
        release_fetcher_mock : PyPiReleaseFetcher = Mock()
        release_fetcher_mock.fetch.return_value = self.f_session1

        requirement_checker : RequirementChecker = RequirementChecker(
            release_fetcher = release_fetcher_mock
        )
        actual : list[RequirementDetail] = requirement_checker._RequirementChecker__create_requirement_details(l_session = self.l_session1, only_stable_releases = False, waiting_time = 0) # type: ignore
        
        # Assert
        self.assertTrue(
            SupportMethodProvider.are_lists_of_requirementdetails_equal(
                list1 = actual,
                list2 = self.expected_sd1
            ))
    def test_calculateprc_shouldreturnexpectedstring_wheninvoked(self) -> None:
        
        # Arrange
        value : int = 5
        total : int = 10
        expected : str = "50.00%"
        
        # Act
        requirement_checker : RequirementChecker = RequirementChecker()
        actual : str = requirement_checker._RequirementChecker__calculate_prc(value = value, total = total) # type: ignore
        
        # Assert
        self.assertEqual(actual, expected)  

    def test_getsummary_shouldraiseexpectedexceptionandmessage_whenwaitingtimelessthanminimum(self):
        
        # Arrange
        file_path : str = r"C:/Dockerfile"
        waiting_time : int = 2
        minimum_wt : int = 5
        expected : str = _MessageCollection.waiting_time_cant_be_less_than(waiting_time, minimum_wt)

        # Act, Assert
        with self.assertRaises(expected_exception = Exception, msg = expected):
            requirement_checker : RequirementChecker = RequirementChecker()
            requirement_checker.get_summary(file_path = file_path, waiting_time = waiting_time)
    def test_getsummary_shouldreturnexpectedrequirementsummary_wheninvoked(self):
        
        # Arrange
        requirement_summary : RequirementSummary = ObjectMother.get_requirement_summary()
        packages : list[Package] = [detail.current_package for detail in requirement_summary.details]
        l_session : LSession = LSession(packages = packages, unparsed_lines = [])

        f_sessions : list[FSession] = []
        for detail in requirement_summary.details:
            f_session : FSession = FSession(
                package_name = detail.current_package.name,
                most_recent_release = detail.most_recent_release,
                releases = [detail.most_recent_release],
                xml_items = [],
                badges = None
            )
            f_sessions.append(f_session)

        package_loader : MagicMock = MagicMock(spec = LocalPackageLoader)
        package_loader.load.return_value = l_session

        release_fetcher : MagicMock = MagicMock(spec = PyPiReleaseFetcher)
        release_fetcher.fetch.side_effect = f_sessions

        sleeping_function : MagicMock = MagicMock()

        file_path : str = r"C:/Dockerfile"
        only_stable_releases : bool = False
        waiting_time : int = 5

        # Act
        requirement_checker : RequirementChecker = RequirementChecker(
            package_loader = package_loader,
            release_fetcher = release_fetcher,
            sleeping_function = sleeping_function
        )
        
        with patch("os.path.isfile", return_value = True):
            actual : RequirementSummary = requirement_checker.get_summary(
                file_path = file_path, 
                only_stable_releases = only_stable_releases, 
                waiting_time = waiting_time
            )

        # Assert
        self.assertEqual(actual.total_packages, requirement_summary.total_packages)
        self.assertEqual(actual.matching, requirement_summary.matching)
        self.assertEqual(actual.matching_prc, requirement_summary.matching_prc)
        self.assertEqual(len(actual.details), len(requirement_summary.details))
        package_loader.load.assert_called_once_with(file_path = file_path)
    def test_getstatus_shouldreturnformattedstring_wheninvoked(self):

        # Arrange
        file_path : str = r"C:/Dockerfile"
        requirement_summary : RequirementSummary = ObjectMother.get_requirement_summary()
        formatter : MagicMock = MagicMock(spec = Formatter)
        expected : str = "Formatted Summary"
        formatter.format_requirement_summary.return_value = expected

        # Act
        requirement_checker : RequirementChecker = RequirementChecker(formatter = formatter)
        
        with patch.object(RequirementChecker, 'get_summary', return_value = requirement_summary):
            actual : str = requirement_checker.get_status(file_path)

        # Assert
        self.assertEqual(actual, expected)
        formatter.format_requirement_summary.assert_called_once_with(requirement_summary)
    def test_trygetstatus_shouldreturnexceptionmessage_whenexceptionisraised(self):
        
        # Arrange
        file_path : str = r"C:/Dockerfile"
        error_message : str = "File not found."
        
        # Act       
        with patch.object(RequirementChecker, 'get_status', side_effect = Exception(error_message)):
            actual : str = RequirementChecker().try_get_status(file_path = file_path)
        
        # Assert
        self.assertEqual(actual, error_message)

# MAIN
if __name__ == "__main__":
    result = unittest.main(argv=[''], verbosity=3, exit=False)