# GLOBAL MODULES
import os
import sys
import unittest
from datetime import datetime
from parameterized import parameterized
from requests import Response
from time import time
from typing import Any, Optional, Callable, Tuple, cast
from unittest.mock import Mock, patch, mock_open, MagicMock

# LOCAL MODULES
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))
from nwpackageversions import _MessageCollection, LSession, LambdaCollection, LocalPackageLoader, Package
from nwpackageversions import PyPiReleaseFetcher, RequirementChecker, RequirementDetail, RequirementSummary, XMLItem, Release, FSession

# SUPPORT METHODS
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
    def are_RequirementDetails_equal(sd1 : RequirementDetail, sd2 : RequirementDetail) -> bool:

        '''Returns True if all the fields of the two objects contain the same values.'''

        return (
            SupportMethodProvider.are_packages_equal(sd1.current_package, sd2.current_package) and
            SupportMethodProvider.are_releases_equal(sd1.most_recent_release, sd2.most_recent_release) and
            sd1.is_version_matching == sd2.is_version_matching and
            sd1.description == sd2.description
            )
    @staticmethod
    def are_lists_of_RequirementDetails_equal(list1 : list[RequirementDetail], list2 : list[RequirementDetail]) -> bool:

        '''Returns True if all the items of list1 contain the same values of the corresponding items of list2.'''

        return SupportMethodProvider.__are_lists_equal(
                list1 = list1, 
                list2 = list2, 
                comparer = lambda sd1, sd2 : SupportMethodProvider.are_RequirementDetails_equal(sd1, sd2)
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
            SupportMethodProvider.are_lists_of_xmlitems_equal(fs1.xml_items, fs2.xml_items)
            )

# TEST CLASSES
class XMLItemTestCase(unittest.TestCase):

    def setUp(self) -> None:

        self.title : Optional[str] = "2.1.2"
        self.link : Optional[str] = "https://pypi.org/project/numpy/2.1.2/"
        self.description : Optional[str] = "Fundamental package for array computing in Python"
        self.author : Optional[str] = "stephen@hotmail.com"
        self.pubdate : Optional[datetime] = datetime(2024, 10, 5, 18, 28, 18)
        self.pubdate_str : Optional[str] = "Sat, 05 Oct 2024 18:28:18 GMT"
    def test_xmlitem_shouldinitializeasexpected_wheninvoked(self) -> None:
        
        # Arrange
        # Act
        xml_item : XMLItem = XMLItem(
            title = self.title,
            link = self.link,
            description = self.description,
            author = self.author,
            pubdate = self.pubdate,
            pubdate_str = self.pubdate_str
        )

        # Assert
        self.assertEqual(xml_item.title, self.title)
        self.assertEqual(xml_item.link, self.link)
        self.assertEqual(xml_item.description, self.description)
        self.assertEqual(xml_item.author, self.author)
        self.assertEqual(xml_item.pubdate, self.pubdate)
        self.assertEqual(xml_item.pubdate_str, self.pubdate_str)
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
        xml_item : XMLItem = XMLItem(
            title = self.title,
            link = self.link,
            description = self.description,
            author = self.author,
            pubdate = self.pubdate,
            pubdate_str = self.pubdate_str
        )		
        actual_str : str = str(xml_item)
        actual_repr : str = repr(xml_item)
        
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
    def test_release_shouldinitializeasexpected_wheninvoked(self) -> None:
        
		# Arrange       
        # Act
        release : Release = Release(
			package_name = self.package_name, 
			version = self.version, 
			date = self.date
		)
        
        # Assert
        self.assertEqual(release.package_name, self.package_name)
        self.assertEqual(release.version, self.version)
        self.assertEqual(release.date, self.date)
    def test_release_shouldreturnexpectedstring_wheninvoked(self) -> None:
        
		# Arrange
        expected : str = "{ 'package_name': 'numpy', 'version': '2.1.2', 'date': '2024-10-05' }"
        
        # Act
        release : Release = Release(
			package_name = self.package_name, 
			version = self.version, 
			date = self.date
		)		
        actual_str : str = str(release)
        actual_repr : str = repr(release)
        
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

        self.xml_items: list[XMLItem] = [
            XMLItem(title="2.1.2", link="https://pypi.org/project/numpy/2.1.2/", description="Fundamental package for array computing in Python", author=None, pubdate=datetime.strptime("Sat, 05 Oct 2024 18:28:18 GMT", "%a, %d %b %Y %H:%M:%S %Z"), pubdate_str="Sat, 05 Oct 2024 18:28:18 GMT"),
            XMLItem(title="2.1.1", link="https://pypi.org/project/numpy/2.1.1/", description="Fundamental package for array computing in Python", author=None, pubdate=datetime.strptime("Tue, 03 Sep 2024 15:01:06 GMT", "%a, %d %b %Y %H:%M:%S %Z"), pubdate_str="Tue, 03 Sep 2024 15:01:06 GMT"),
            XMLItem(title="2.0.2", link="https://pypi.org/project/numpy/2.0.2/", description="Fundamental package for array computing in Python", author=None, pubdate=datetime.strptime("Mon, 26 Aug 2024 20:04:14 GMT", "%a, %d %b %Y %H:%M:%S %Z"), pubdate_str="Mon, 26 Aug 2024 20:04:14 GMT"),
            XMLItem(title="2.1.0", link="https://pypi.org/project/numpy/2.1.0/", description="Fundamental package for array computing in Python", author=None, pubdate=datetime.strptime("Sun, 18 Aug 2024 21:39:07 GMT", "%a, %d %b %Y %H:%M:%S %Z"), pubdate_str="Sun, 18 Aug 2024 21:39:07 GMT")
        ]
    def test_fsession_shouldinitializeasexpected_wheninvoked(self):
	
		# Arrange
        # Act
        f_session : FSession = FSession(
            package_name = self.package_name,
            most_recent_release = self.most_recent_release,
            releases = self.releases,
            xml_items = self.xml_items
        )
		
		# Assert
        self.assertEqual(f_session.package_name, self.package_name)
        self.assertEqual(f_session.most_recent_release.package_name, self.most_recent_release.package_name)
        self.assertEqual(f_session.most_recent_release.version, self.most_recent_release.version)
        self.assertEqual(f_session.most_recent_release.date, self.most_recent_release.date)
        self.assertEqual(f_session.releases, self.releases)
        self.assertEqual(f_session.xml_items, self.xml_items)
    def test_fsession_shouldreturnexpectedstring_whenargumentsarenotnone(self):
        
		# Arrange
        expected: str = (
            "{ 'package_name': 'numpy', "
            f"'most_recent_release': '{self.mrr_formatter(self.most_recent_release)}', "
            "'releases': '4', "
            "'xml_items': '4' }"
        )		
		
        # Act
        f_session : FSession = FSession(
            package_name = self.package_name,
            most_recent_release = self.most_recent_release,
            releases = self.releases,
            xml_items = self.xml_items
        )
        actual : str = str(f_session)

        # Assert
        self.assertEqual(actual, expected)
class LambdaCollectionTestCase(unittest.TestCase):

    def test_getfunction_shouldreturnexpectedstatuscodeandtext_wheninvoked(self):
	
        # Arrange
        expected_sc : int = 200
        expected_text : str = '<rss version="2.0"></rss>'
        response_mock : Response = MagicMock(spec = Response)
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
    def test_listloggingfunction_shouldlogitemsasexpected_whenlistisprovided(self) -> None:
        
        # Arrange
        lst : list[Any] = [1, 2, 3]
        messages : list[str] = []
        logging_function_mock : Callable[[str], None] = lambda msg : messages.append(msg)

        # Act, 
        list_logging_function : Callable[[Callable[[str], None], list[Any]], None] = LambdaCollection.list_logging_function()
        list_logging_function(logging_function_mock, lst)
        
        # Assert
        self.assertEqual(messages, ["1", "2", "3"])
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
    def test_lsession_shouldinitializeasexpected_wheninvoked(self):
	
		# Arrange
        # Act
        l_session : LSession = LSession(
            packages = self.packages,
            unparsed_lines = self.unparsed_lines
        )
		
		# Assert
        self.assertTrue(
            SupportMethodProvider.are_lists_of_packages_equal(
                list1 = l_session.packages,
                list2 = self.packages
            ))
        self.assertEqual(l_session.unparsed_lines, self.unparsed_lines)
    def test_lsession_shouldreturnexpectedstring_wheninvoked(self):
        
		# Arrange
        expected: str = (
                "{ "
                f"'packages': '{len(self.packages)}', "
                f"'unparsed_lines': '{len(self.unparsed_lines)}'"
                " }"                
            )		
		
        # Act
        l_session : LSession = LSession(
            packages = self.packages,
            unparsed_lines = self.unparsed_lines
        )
        actual : str = str(l_session)

        # Assert
        self.assertEqual(actual, expected)
class RequirementDetailTestCase(unittest.TestCase):

    def setUp(self) -> None:

        self.package1 : Package = Package(name = "requests", version = "2.26.0")
        self.release1 : Release = Release(package_name = "requests", version = "2.26.0", date = datetime(2023, 10, 5))
        self.is_version_matching1 : bool = True
        self.description1 : str = "The current version matches the most recent release."

        self.package2 : Package = Package(name = "numpy", version = "1.26.3")
        self.release2 : Release = Release(package_name = "numpy", version = "2.1.2", date = datetime(2024, 10, 5))
        self.is_version_matching2 : bool = False
        self.description2 : str = (
            "The current version ('1.26.3') of 'numpy' doesn't match with the most recent release "
            "('2.1.2', '2024-10-05')."
        )
        self.expected2 : str = "{ 'description': 'The current version ('1.26.3') of 'numpy' doesn't match with the most recent release ('2.1.2', '2024-10-05').' }"
    def test_requirementdetail_shouldinitializeasexpected_wheninvoked(self) -> None:
	
        # Arrange
        # Act
        requirement_detail : RequirementDetail = RequirementDetail(
            current_package = self.package1,
            most_recent_release = self.release1,
            is_version_matching = self.is_version_matching1,
            description = self.description1
        )

        # Assert
        self.assertEqual(requirement_detail.current_package, self.package1)
        self.assertEqual(requirement_detail.most_recent_release, self.release1)
        self.assertTrue(requirement_detail.is_version_matching)
        self.assertEqual(requirement_detail.description, self.description1)
    def test_requirementdetail_shouldreturnexpectedstring_wheninvoked(self) -> None:
        
		# Arrange
        requirement_detail : RequirementDetail = RequirementDetail(
            current_package = self.package2,
            most_recent_release = self.release2,
            is_version_matching = self.is_version_matching2,
            description = self.description2
        )

        # Act
        actual_str : str = str(requirement_detail)
        actual_repr : str = requirement_detail.__repr__()

        # Assert
        self.assertEqual(actual_str, self.expected2)
        self.assertEqual(actual_repr, self.expected2)
class RequirementSummaryTestCase(unittest.TestCase):

    def setUp(self) -> None:
        
        self.package1 : Package = Package(name = "black", version = "22.12.0")
        self.release1 : Release = Release(package_name = "black", version = "22.12.0", date = datetime(2024, 5, 15))
        self.is_version_matching1 : bool = True
        self.description1 : str = "The current version matches the most recent release."
		
        self.requirement_detail1 : RequirementDetail = RequirementDetail(
            current_package = self.package1,
            most_recent_release = self.release1,
            is_version_matching = self.is_version_matching1,
            description = self.description1
        )
        
        self.package2 : Package = Package(name = "opencv-python", version = "4.5.0")
        self.release2 : Release = Release(package_name = "opencv-python", version = "4.10.0", date = datetime(2023, 8, 12))
        self.is_version_matching2 : bool = False
        self.description2 : str = "The current version ('4.5.0') of 'opencv-python' doesn't match with the most recent release ('4.10.0', '2023-08-12')."
		
        self.requirement_detail2 : RequirementDetail = RequirementDetail(
            current_package = self.package2,
            most_recent_release = self.release2,
            is_version_matching = self.is_version_matching2,
            description = self.description2
        )

        self.total_packages : int = 2
        self.matching : int = 1
        self.matching_prc : str = "50.00%"
        self.mismatching : int = 1
        self.mismatching_prc : str = "50.00%"
        self.details : list[RequirementDetail] = [
			self.requirement_detail1, 
			self.requirement_detail2
		]

        self.expected : str = "{ 'total_packages': '2', 'matching': '1', 'matching_prc': '50.00%', 'mismatching': '1', 'mismatching_prc': '50.00%' }"
    def test_requirementsummary_shouldinitializeasexpected_wheninvoked(self) -> None:
	
        # Arrange
        # Act
        requirement_summary : RequirementSummary = RequirementSummary(
            total_packages = self.total_packages,
            matching = self.matching,
            matching_prc = self.matching_prc,
            mismatching = self.mismatching,
            mismatching_prc = self.mismatching_prc,
            details = self.details
        )

        # Assert
        self.assertEqual(requirement_summary.total_packages, self.total_packages)
        self.assertEqual(requirement_summary.matching, self.matching)
        self.assertEqual(requirement_summary.matching_prc, self.matching_prc)
        self.assertEqual(requirement_summary.mismatching, self.mismatching)
        self.assertEqual(requirement_summary.mismatching_prc, self.mismatching_prc)
        self.assertEqual(len(requirement_summary.details), len(self.details))
        self.assertTrue(
            SupportMethodProvider.are_lists_of_RequirementDetails_equal(
                list1 = requirement_summary.details,
                list2 = self.details
            ))
    def test_requirementsummary_shouldreturnexpectedstring_wheninvoked(self) -> None:
        
		# Arrange
        requirement_summary : RequirementSummary = RequirementSummary(
            total_packages = self.total_packages,
            matching = self.matching,
            matching_prc = self.matching_prc,
            mismatching = self.mismatching,
            mismatching_prc = self.mismatching_prc,
            details = self.details
        )

        # Act
        actual : str = str(requirement_summary)

        # Assert
        self.assertEqual(actual, self.expected) 
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
    
    def test_fetch_shouldraiseexception_whenxmlitemsarezero(self) -> None:
        
        # Arrange
        xml_content : str = self.xml_content.replace("<title>2.2.3</title>", "<title></title>")
        xml_content = xml_content.replace("<pubDate>Wed, 10 Apr 2024 19:44:10 GMT</pubDate>", "")       
        xml_response : Response = Mock()
        xml_response.text = xml_content

        get_function_mock : Callable[[str], Response] = Mock(return_value = xml_response)
        msg : str = _MessageCollection.no_suitable_xml_items_found(url = "https://pypi.org/rss/project/pandas/releases.xml")

        # Act, Assert
        with self.assertRaises(expected_exception = Exception, msg = msg):
            release_fetcher : PyPiReleaseFetcher = PyPiReleaseFetcher(get_function = get_function_mock)
            release_fetcher.fetch(package_name = "pandas")
    def test_fetch_shouldreturnexpectedfsession_wheninvoked(self) -> None:
        
        # Arrange
        expected : FSession = FSession(
            package_name = "pandas",
            most_recent_release = self.releases[0],
            releases = self.releases,
            xml_items = self.xml_items
        )
        
        # Act
        release_fetcher : PyPiReleaseFetcher = PyPiReleaseFetcher(get_function = self.get_function_mock)
        actual : FSession = release_fetcher.fetch(package_name = "pandas")

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
    def test_requirementchecker_shouldreturnexpectedtuple_whenversionsmatch(self) -> None:
        
        # Arrange
        # Act
        requirement_checker : RequirementChecker = RequirementChecker()
        actual : Tuple[bool, str] = requirement_checker._RequirementChecker__compare(current_package = self.package1, most_recent_release = self.release1) # type: ignore
        
        # Assert
        self.assertEqual(actual, self.expected_tpl1)
    def test_requirementchecker_shouldreturnexpectedtuple_whenversionsmismatch(self) -> None:
        
        # Arrange
        # Act
        requirement_checker : RequirementChecker = RequirementChecker()
        actual : Tuple[bool, str] = requirement_checker._RequirementChecker__compare(current_package = self.package2, most_recent_release = self.release2) # type: ignore
        
        # Assert
        self.assertEqual(actual, self.expected_tpl2)
    def test_createrequirementdetails_shouldreturnexpectedlistofrequirementdetails_wheninvoked(self) -> None:
        
        # Arrange
        # Act
        requirement_checker : RequirementChecker = RequirementChecker()
        actual : list[RequirementDetail] = requirement_checker._RequirementChecker__create_requirement_details(l_session = self.l_session1, waiting_time = 0) # type: ignore
        
        # Assert
        self.assertTrue(
            SupportMethodProvider.are_lists_of_RequirementDetails_equal(
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
    def test_check_shouldraiseexpectedexceptionandmessage_whenwaitingtimelessthanminimum(self):
        
        # Arrange
        file_path : str = r"C:/Dockerfile"
        waiting_time : int = 2
        minimum_wt : int = 5
        expected : str = _MessageCollection.waiting_time_cant_be_less_than(waiting_time, minimum_wt)

        # Act, Assert
        with self.assertRaises(expected_exception = Exception, msg = expected):
            requirement_checker : RequirementChecker = RequirementChecker()
            requirement_checker.check(file_path = file_path, waiting_time = waiting_time)
    def test_check_shouldreturnexpectedrequirementsummaryandlogexpectedmessages_wheninvoked(self):
        
        # Arrange
        packages : list[Package] = [
            Package(name = "requests", version = "2.26.0"),
            Package(name = "black", version = "22.12.0")
        ]
        l_session: LSession = LSession(packages = packages, unparsed_lines = [])

        release1 : Release = Release(package_name = "requests", version = "2.26.0", date = datetime(2024, 1, 1))
        release2 : Release = Release(package_name = "black", version = "22.12.0", date = datetime(2024, 1, 2))      
        f_session_1: FSession = FSession(package_name = "requests", most_recent_release = release1, releases = [ release1 ], xml_items = [])
        f_session_2: FSession = FSession(package_name = "black", most_recent_release = release2, releases = [ release2 ], xml_items = [])

        package_loader_mock : LocalPackageLoader = Mock()
        package_loader_mock.load.return_value = l_session

        release_fetcher_mock : PyPiReleaseFetcher = Mock()
        release_fetcher_mock.fetch.side_effect = [ f_session_1, f_session_2 ]

        messages: list[str] = []
        logging_function_mock : Callable[[str], None] = lambda msg : messages.append(msg)
        sleeping_function_mock : Callable[[int], None] = lambda x : None

        file_path : str = r"C:/Dockerfile"
        waiting_time : int = 5

        descriptions : list[str] = [
            "{ 'description': 'The current version ('2.26.0') of 'requests' matches with the most recent release ('2.26.0', '2024-01-01').' }",
            "{ 'description': 'The current version ('22.12.0') of 'black' matches with the most recent release ('22.12.0', '2024-01-02').' }"
        ]
        expected : RequirementSummary = RequirementSummary(
            total_packages = 2,
            matching = 2,
            matching_prc = "100.00%",
            mismatching = 0,
            mismatching_prc = "0.00%",
            details = [ 
                Mock(description = descriptions[0]), 
                Mock(description = descriptions[1])
            ]
        )

        expected_messages: list[str] = [
            _MessageCollection.status_checking_operation_started(),
            _MessageCollection.list_local_packages_will_be_loaded(file_path),
            _MessageCollection.waiting_time_will_be(waiting_time),
            _MessageCollection.x_local_packages_found_successfully_loaded(l_session.packages),
            _MessageCollection.x_unparsed_lines(l_session.unparsed_lines),
            _MessageCollection.starting_to_evaluate_status_local_package(),
            _MessageCollection.status_evaluation_operation_successfully_loaded(),
            descriptions[0],
            descriptions[1],
            _MessageCollection.starting_creation_requirement_summary(),
            _MessageCollection.requirement_summary_successfully_created(),
            str(expected),
            _MessageCollection.status_checking_operation_completed()
        ]        

        # Act
        requirement_checker : RequirementChecker = RequirementChecker(
            package_loader = package_loader_mock,
            release_fetcher = release_fetcher_mock,
            logging_function = logging_function_mock,
            list_logging_function = LambdaCollection.list_logging_function(),
            sleeping_function = sleeping_function_mock

        )
        actual : RequirementSummary = requirement_checker.check(file_path = file_path, waiting_time = waiting_time)

        # Assert
        self.assertEqual(actual.total_packages, expected.total_packages)
        self.assertEqual(actual.matching, expected.matching)
        self.assertEqual(actual.matching_prc, expected.matching_prc)        
        self.assertEqual(actual.mismatching, expected.mismatching)
        self.assertEqual(actual.mismatching_prc, expected.mismatching_prc)
        self.assertEqual(messages, expected_messages)
    def test_trycheck_shouldreturnnoneandlogexpectedmessage_whenraisedexception(self):
        
        # Arrange
        file_path : str = r"C:/Dockerfile"
        waiting_time : int = 2
        minimum_wt : int = 5
        expected : str = _MessageCollection.waiting_time_cant_be_less_than(waiting_time, minimum_wt)

        messages : list[str] = []
        logging_function_mock : Callable[[str], None] = lambda msg : messages.append(msg)

        # Act
        requirement_checker : RequirementChecker = RequirementChecker(
            package_loader = LocalPackageLoader(),
            release_fetcher = PyPiReleaseFetcher(),
            logging_function = logging_function_mock,
            list_logging_function = LambdaCollection.list_logging_function(),
            sleeping_function = LambdaCollection.sleeping_function()

        )
        requirement_summary : Optional[RequirementSummary] = requirement_checker.try_check(file_path = file_path, waiting_time = waiting_time)
        
        # Assert
        self.assertIsNone(requirement_summary)
        self.assertEqual(messages[0], expected)
    def test_logrequirementsummary_shouldlogexpectedmessages_wheninvoked(self):

        # Arrange
        messages: list[str] = []
        logging_function_mock : Callable[[str], None] = lambda msg : messages.append(msg)

        descriptions : list[str] = [
            "{ 'description': 'The current version ('2.26.0') of 'requests' matches with the most recent release ('2.26.0', '2024-01-01').' }",
            "{ 'description': 'The current version ('22.12.0') of 'black' matches with the most recent release ('22.12.0', '2024-01-02').' }"
        ]
        requirement_summary : RequirementSummary = RequirementSummary(
            total_packages = 2,
            matching = 2,
            matching_prc = "100.00%",
            mismatching = 0,
            mismatching_prc = "0.00%",
            details = [ 
                RequirementDetail(
                    current_package = Mock(), 
                    most_recent_release = Mock(), 
                    is_version_matching = True, 
                    description = "The current version ('2.26.0') of 'requests' matches with the most recent release ('2.26.0', '2024-01-01')."
                ),
                RequirementDetail(
                    current_package = Mock(), 
                    most_recent_release = Mock(), 
                    is_version_matching = True, 
                    description = "The current version ('22.12.0') of 'black' matches with the most recent release ('22.12.0', '2024-01-02')."
                )
            ]
        )

        expected: list[str] = [
            str(requirement_summary),
            descriptions[0],
            descriptions[1]            
        ]

        # Act
        requirement_checker : RequirementChecker = RequirementChecker(
            package_loader = LocalPackageLoader(),
            release_fetcher = PyPiReleaseFetcher(),
            logging_function = logging_function_mock,
            list_logging_function = LambdaCollection.list_logging_function(),
            sleeping_function = LambdaCollection.sleeping_function()

        )
        requirement_checker.log_requirement_summary(requirement_summary = requirement_summary)

        # Assert
        self.assertEqual(messages, expected)
    def test_getdefaultdevcointainerdockerfilepath_shouldreturnexpectedpath_wheninvoked(self) -> None:
        
        # Arrange
        expected: str = os.path.join("/path/.devcontainer", "Dockerfile")

        # Act, Assert
        with patch('os.path.abspath') as mock_abspath:

            mock_abspath.return_value = r"/path/src"

            requirement_checker : RequirementChecker = RequirementChecker()
            actual : str = requirement_checker.get_default_devcointainer_dockerfile_path()

            self.assertEqual(actual, expected)

# Main
if __name__ == "__main__":
    result = unittest.main(argv=[''], verbosity=3, exit=False)