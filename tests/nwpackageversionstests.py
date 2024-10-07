# GLOBAL MODULES
import os
import sys
import unittest
from datetime import datetime
from typing import Optional

# LOCAL MODULES
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))
from nwpackageversions import XMLItem, Release

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

# Main
if __name__ == "__main__":
    result = unittest.main(argv=[''], verbosity=3, exit=False)