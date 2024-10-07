# GLOBAL MODULES
import os
import sys
import unittest
from datetime import datetime
from typing import Optional

# LOCAL MODULES
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))
from nwpackageversions import XMLItem

# SUPPORT METHODS
# TEST CLASSES
class XMLItemTestCase(unittest.TestCase):

    def test_xmlitem_shouldinitializeasexpected_wheninvoked(self) -> None:
        
        # Arrange
        title : Optional[str] = "2.1.2"
        link : Optional[str] = "https://pypi.org/project/numpy/2.1.2/"
        description : Optional[str] = "Fundamental package for array computing in Python"
        author : Optional[str] = None
        pubdate : Optional[datetime] = datetime(2024, 10, 5, 18, 28, 18)
        pubdate_str : Optional[str] = "Sat, 05 Oct 2024 18:28:18 GMT"

        # Act
        xml_item : XMLItem = XMLItem(
            title = title,
            link = link,
            description = description,
            author = author,
            pubdate = pubdate,
            pubdate_str = pubdate_str
        )

        # Assert
        self.assertEqual(xml_item.title, title)
        self.assertEqual(xml_item.link, link)
        self.assertEqual(xml_item.description, description)
        self.assertEqual(xml_item.author, author)
        self.assertEqual(xml_item.pubdate, pubdate)
        self.assertEqual(xml_item.pubdate_str, pubdate_str)

# Main
if __name__ == "__main__":
    result = unittest.main(argv=[''], verbosity=3, exit=False)