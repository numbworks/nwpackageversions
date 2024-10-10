# GLOBAL MODULES
import os
import sys
import unittest
from datetime import datetime
from requests import Response
from typing import Optional, Callable, cast
from unittest.mock import patch, mock_open, MagicMock

# LOCAL MODULES
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))
from nwpackageversions import LambdaCollection, XMLItem, Release, FSession

# SUPPORT METHODS
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

        self.package_name = "numpy"

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
            "'most_recent_version': '2.1.2', "
            "'most_recent_date': '2024-10-05', "
            "'releases': '4', "
            "'xml_items': '4' }"
        )		
		
        # Act
        f_session : FSession = FSession(
            package_name = self.package_name,
            most_recent_version = self.most_recent_version,
            most_recent_date = self.most_recent_date,
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

# Main
if __name__ == "__main__":
    result = unittest.main(argv=[''], verbosity=3, exit=False)