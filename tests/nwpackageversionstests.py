# GLOBAL MODULES
import os
import sys
import unittest
from datetime import datetime
from typing import Optional

# LOCAL MODULES
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))
from nwpackageversions import PyPiRelease

# SUPPORT METHODS
# TEST CLASSES
class PyPiReleaseTestCase(unittest.TestCase):

    def test_pypirelease_shouldinitializeasexpected_wheninvoked(self) -> None:
        
        # Arrange
        title : Optional[str] = "2.1.2"
        link : Optional[str] = "https://pypi.org/project/numpy/2.1.2/"
        description : Optional[str] = "Fundamental package for array computing in Python"
        author : Optional[str] = None
        pubdate : Optional[datetime] = datetime(2024, 10, 5, 18, 28, 18)
        pubdate_str : Optional[str] = "Sat, 05 Oct 2024 18:28:18 GMT"

        # Act
        release : PyPiRelease = PyPiRelease(
            title = title,
            link = link,
            description = description,
            author = author,
            pubdate = pubdate,
            pubdate_str = pubdate_str
        )

        # Assert
        self.assertEqual(release.title, title)
        self.assertEqual(release.link, link)
        self.assertEqual(release.description, description)
        self.assertEqual(release.author, author)
        self.assertEqual(release.pubdate, pubdate)
        self.assertEqual(release.pubdate_str, pubdate_str)

# Main
if __name__ == "__main__":
    result = unittest.main(argv=[''], verbosity=3, exit=False)