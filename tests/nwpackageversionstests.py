# GLOBAL MODULES
import os
import sys
from time import time
import unittest
from datetime import datetime
from parameterized import parameterized
from requests import Response
from typing import Any, Optional, Callable, cast
from unittest.mock import Mock, patch, mock_open, MagicMock

# LOCAL MODULES
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))
from nwpackageversions import LSession, LambdaCollection, LocalPackageLoader, Package, StatusDetail, StatusSummary, XMLItem, Release, FSession

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
    def are_statusdetails_equal(sd1 : StatusDetail, sd2 : StatusDetail) -> bool:

        '''Returns True if all the fields of the two objects contain the same values.'''

        return (
            SupportMethodProvider.are_packages_equal(sd1.current_package, sd2.current_package) and
            SupportMethodProvider.are_releases_equal(sd1.most_recent_release, sd2.most_recent_release) and
            sd1.is_version_matching == sd2.is_version_matching and
            sd1.description == sd2.description
            )
    @staticmethod
    def are_lists_of_statusdetails_equal(list1 : list[StatusDetail], list2 : list[StatusDetail]) -> bool:

        '''Returns True if all the items of list1 contain the same values of the corresponding items of list2.'''

        return SupportMethodProvider.__are_lists_equal(
                list1 = list1, 
                list2 = list2, 
                comparer = lambda p1,p2 : SupportMethodProvider.are_statusdetails_equal(p1, p2)
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

        # Act, Assert
        with patch('nwpackageversions.LambdaCollection.logging_function', return_value = lambda msg : messages.append(msg)):

            logging_function : Callable[[list[Any]], None] = LambdaCollection.list_logging_function()
            logging_function(lst)
           
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
class StatusDetailTestCase(unittest.TestCase):

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
    def test_statusdetail_shouldinitializeasexpected_wheninvoked(self) -> None:
	
        # Arrange
        # Act
        status_detail : StatusDetail = StatusDetail(
            current_package = self.package1,
            most_recent_release = self.release1,
            is_version_matching = self.is_version_matching1,
            description = self.description1
        )

        # Assert
        self.assertEqual(status_detail.current_package, self.package1)
        self.assertEqual(status_detail.most_recent_release, self.release1)
        self.assertTrue(status_detail.is_version_matching)
        self.assertEqual(status_detail.description, self.description1)
    def test_statusdetail_shouldreturnexpectedstring_wheninvoked(self) -> None:
        
		# Arrange
        status_detail : StatusDetail = StatusDetail(
            current_package = self.package2,
            most_recent_release = self.release2,
            is_version_matching = self.is_version_matching2,
            description = self.description2
        )

        # Act
        actual_str : str = str(status_detail)
        actual_repr : str = status_detail.__repr__()

        # Assert
        self.assertEqual(actual_str, self.expected2)
        self.assertEqual(actual_repr, self.expected2)
class StatusSummaryTestCase(unittest.TestCase):

    def setUp(self) -> None:
        
        self.package1 : Package = Package(name = "black", version = "22.12.0")
        self.release1 : Release = Release(package_name = "black", version = "22.12.0", date = datetime(2024, 5, 15))
        self.is_version_matching1 : bool = True
        self.description1 : str = "The current version matches the most recent release."
		
        self.status_detail1 : StatusDetail = StatusDetail(
            current_package = self.package1,
            most_recent_release = self.release1,
            is_version_matching = self.is_version_matching1,
            description = self.description1
        )
        
        self.package2 : Package = Package(name = "opencv-python", version = "4.5.0")
        self.release2 : Release = Release(package_name = "opencv-python", version = "4.10.0", date = datetime(2023, 8, 12))
        self.is_version_matching2 : bool = False
        self.description2 : str = "The current version ('4.5.0') of 'opencv-python' doesn't match with the most recent release ('4.10.0', '2023-08-12')."
		
        self.status_detail2 : StatusDetail = StatusDetail(
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
        self.details : list[StatusDetail] = [
			self.status_detail1, 
			self.status_detail2
		]

        self.expected : str = "{ 'total_packages': '2', 'matching': '1', 'matching_prc': '50.00%', 'mismatching': '1', 'mismatching_prc': '50.00%' }"
    def test_statussummary_shouldinitializeasexpected_wheninvoked(self) -> None:
	
        # Arrange
        # Act
        status_summary : StatusSummary = StatusSummary(
            total_packages = self.total_packages,
            matching = self.matching,
            matching_prc = self.matching_prc,
            mismatching = self.mismatching,
            mismatching_prc = self.mismatching_prc,
            details = self.details
        )

        # Assert
        self.assertEqual(status_summary.total_packages, self.total_packages)
        self.assertEqual(status_summary.matching, self.matching)
        self.assertEqual(status_summary.matching_prc, self.matching_prc)
        self.assertEqual(status_summary.mismatching, self.mismatching)
        self.assertEqual(status_summary.mismatching_prc, self.mismatching_prc)
        self.assertEqual(len(status_summary.details), len(self.details))
        self.assertTrue(
            SupportMethodProvider.are_lists_of_statusdetails_equal(
                list1 = status_summary.details,
                list2 = self.details
            ))
    def test_statussummary_shouldreturnexpectedstring_wheninvoked(self) -> None:
        
		# Arrange
        status_summary : StatusSummary = StatusSummary(
            total_packages = self.total_packages,
            matching = self.matching,
            matching_prc = self.matching_prc,
            mismatching = self.mismatching,
            mismatching_prc = self.mismatching_prc,
            details = self.details
        )

        # Act
        actual : str = str(status_summary)

        # Assert
        self.assertEqual(actual, self.expected) 
class LocalPackageLoaderTestCase(unittest.TestCase):

    def setUp(self) -> None:

        self.file_reader_mock: Callable[[str], str] = Mock(return_value = "content")

    def test_localpackageloader_shouldinitializeasexpected_wheninvoked(self) -> None:
        
        # Arrange
        file_reader_function: Callable[[str], str] = LambdaCollection.file_reader_function()

        # Act
        package_loader : LocalPackageLoader = LocalPackageLoader(file_reader_function = file_reader_function)

        # Assert
        self.assertIsInstance(package_loader, LocalPackageLoader)
    def test_cleanunparsedlines_shouldremovermptystrings_whenlinesprovided(self) -> None:
        
        # Arrange
        package_loader : LocalPackageLoader = LocalPackageLoader(file_reader_function = self.file_reader_mock)
        unparsed_lines : list[str] = ["line1", "", "line2", ""]
        expected : list[str] = ["line1", "line2"]

        # Act
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
        package_loader : LocalPackageLoader = LocalPackageLoader(file_reader_function = self.file_reader_mock)

        # Act
        actual : bool = package_loader._LocalPackageLoader__is_requirements(file_path) # type: ignore

        # Assert
        self.assertEqual(actual, expected)

# Main
if __name__ == "__main__":
    result = unittest.main(argv=[''], verbosity=3, exit=False)