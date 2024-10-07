'''
A module that helps with retrieving package information from PyPi.org.

Alias: nwpv
'''

# GLOBAL MODULES
import copy
import re
import requests
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from datetime import datetime
from functools import lru_cache
from re import Match
from requests import Response
from typing import Any, Callable, Literal, Optional, Tuple, cast
from xml.etree.ElementTree import Element

# LOCAL MODULES
# CONSTANTS
# DTOs
@dataclass(frozen = True)
class XMLItem():

    '''Represents the content of a <item></item> taken from a PyPi.org's releases.xml file.'''

    title : Optional[str]
    link : Optional[str]
    description : Optional[str]
    author : Optional[str]
    pubdate : Optional[datetime]
    pubdate_str : Optional[str]

    def __str__(self):
        return str(
                "{ "
                f"'title': '{self.title}', "
                f"'link': '{self.link}', "
                f"'description': '{self.description}', "
                f"'author': '{self.author}', "                                
                f"'pubdate_str': '{self.pubdate_str}'"
                " }"                
            )
    def __repr__(self):
        return self.__str__()
@dataclass(frozen = True)
class Release():

    '''Represents a release on PyPi.org. It's a subset of XMLItem.'''

    package_name : str
    version : str
    date : datetime

    def __str__(self):
        return str(
                "{ "
                f"'package_name': '{self.package_name}', "
                f"'version': '{self.version}', "
                f"'date': '{self.date.strftime("%Y-%m-%d")}'"
                " }"                
            )
    def __repr__(self):
        return self.__str__()
@dataclass(frozen = True)
class Session():

    '''Represents a fetching session performed by PyPiReleaseManager.'''

    package_name : str
    most_recent_version : str
    most_recent_date : datetime
    releases : list[Release]
    xml_items : list[XMLItem]

    def __str__(self):
        return str(
                "{ "
                f"'package_name': '{self.package_name}', "
                f"'most_recent_version': '{self.most_recent_version}', "
                f"'most_recent_date': '{self.most_recent_date.strftime("%Y-%m-%d")}', "
                f"'releases': '{len(self.releases)}', "
                f"'xml_items': '{len(self.xml_items)}'"
                " }"                
            )   
@dataclass(frozen = True)
class Package():

    '''Represents an installed package.'''

    name : str
    version : str

# STATIC CLASSES
# CLASSES
class LambdaCollection():

    '''Provides useful lambda functions.'''

    @staticmethod
    def __load_content(file_path : str) -> str:
        
        '''Reads the content of the provided text file and returns it as string.'''

        content : str = ""
        with open(file_path, 'r', encoding = 'utf-8') as file:
            content = file.read()

        return content

    @staticmethod
    def get_function() -> Callable[[str], Response]:

        '''An adapter around requests.get(url).'''

        return lambda url : requests.get(url)
    @staticmethod
    def logging_function() -> Callable[[str], None]:

        '''An adapter around print().'''

        return lambda msg : print(msg)
    @staticmethod
    def file_reader_function() -> Callable[[str], str]:

        '''An adapter around print().'''

        return lambda file_path : LambdaCollection.__load_content(file_path)    
class PyPiReleaseManager():

    '''This is a client for PyPi release pages.'''

    __get_function : Callable[[str], Response]
    __logging_function : Callable[[str], None]
    __file_reader_function : Callable[[str], str]

    def __init__(
            self, 
            get_function : Callable[[str], Response] = LambdaCollection.get_function(),
            logging_function : Callable[[str], None] = LambdaCollection.logging_function(),
            file_reader_function : Callable[[str], str] = LambdaCollection.file_reader_function()
            ) -> None:
        
        self.__get_function = get_function
        self.__logging_function = logging_function
        self.__file_reader_function = file_reader_function

    def __format_url(self, package_name : str) -> str:

        '''Returns the URL for the package's releases.xml.'''

        url : str =  f"https://pypi.org/rss/project/{package_name}/releases.xml"

        return url  
    def __try_extract_text(self, element : Element, path : str) -> Optional[str]:

        '''Extracts the text from the provided element according to path or returns None.'''

        try:

            result : Optional[Element] = element.find(path = path)

            return cast(Element, result).text

        except:
            return None
    def __try_extract_title(self, element : Element) -> Optional[str]:

        '''Extracts the title from the provided element or returns None.'''

        return self.__try_extract_text(element = element, path = "title")
    def __try_extract_link(self, element : Element) -> Optional[str]:

        '''Extracts the link from the provided element or returns None.'''

        return self.__try_extract_text(element = element, path = "link")
    def __try_extract_description(self, element : Element) -> Optional[str]:

        '''Extracts the description from the provided element or returns None.'''

        return self.__try_extract_text(element = element, path = "description")
    def __try_extract_author(self, element : Element) -> Optional[str]:

        '''Extracts the author from the provided element or returns None.'''

        return self.__try_extract_text(element = element, path = "author")
    def __try_extract_pubdate_str(self, element : Element) -> Optional[str]:

        '''Extracts the pubDate from the provided element or returns None.'''

        return self.__try_extract_text(element = element, path = "pubDate")
    def __parse_pubdate_str(self, pubdate_str : Optional[str]) -> Optional[datetime]:

        '''
            This method expect a dt_str as in the following examples:

                Fri, 20 Sep 2024 13:08:42 GMT
                Wed, 10 Apr 2024 19:44:10 GMT
                Fri, 23 Feb 2024 15:30:19 GMT
                Sat, 20 Jan 2024 02:10:54 GMT
                ...
        '''

        if pubdate_str:

            format : str = "%a, %d %b %Y %H:%M:%S %Z"
            pubdate = datetime.strptime(pubdate_str, format)

            return pubdate
        
        else:
            return None
    def __parse_response(self, response : Response) -> list[XMLItem]:

        '''Convert the provided response to a list of PyPiRelease objects.'''
    
        root : Element = ET.fromstring(text = response.text)

        releases : list[XMLItem] = []
        for channel in root.findall("channel"):
            for item in channel.findall("item"):
                
                title : Optional[str] = self.__try_extract_title(element = item)
                link : Optional[str] = self.__try_extract_link(element = item)
                description : Optional[str] = self.__try_extract_description(element = item)
                author : Optional[str] = self.__try_extract_author(element = item)
                pubdate_str : Optional[str] = self.__try_extract_pubdate_str(element = item)
                pubdate : Optional[datetime] = self.__parse_pubdate_str(pubdate_str = pubdate_str)
                
                release : XMLItem = XMLItem(
                    title = title,
                    link = link,
                    description = description,
                    author = author,
                    pubdate_str = pubdate_str,
                    pubdate = pubdate
                )

                releases.append(release)

        return releases
    def __has_title(self, xml_item : XMLItem) -> bool:

        '''Retuns True if pypi_item.title is not None.'''

        try:

            cast(str, xml_item.title)

            return True

        except:
            return False
    def __has_pubdate(self, xml_item : XMLItem) -> bool:

        '''Retuns True if pypi_item.pubdate is not None.'''

        try:

            cast(datetime, xml_item.pubdate)

            return True

        except:
            return False
    def __filter(self, items : list[Any], function : Callable[[Any], bool]) -> list[Any]:

        '''Runs function on items.'''

        lst : list[Any] = [item for item in items if function(item)]

        return lst
    def __convert_to_release(self, package_name : str, xml_item : XMLItem) -> Release:

        '''Converts the provided xml_item to a Release object.'''

        release : Release = Release(
            package_name = package_name,
            version = cast(str, xml_item.title),
            date = cast(datetime, xml_item.pubdate)
        )

        return release
    def __convert_to_releases(self, package_name : str, xml_items : list[XMLItem]) -> list[Release]:

        '''Converts the provided xml_items to a list of Release objects.'''

        releases : list[Release] = []

        for xml_item in xml_items:
            release : Release = self.__convert_to_release(package_name = package_name, xml_item = xml_item)
            releases.append(release)

        return releases
    def __is_final_release(self, release : Release) -> bool:

        '''
            ['2.1.2', '2.1.1', '2.0.2', '2.1.0']    => True
            ['2.1.0rc1', '7.0.0b1']                 => False
        '''

        pattern : str = r'^\d+\.\d+\.\d+$'
        status : bool = bool(re.match(pattern, release.version))

        return status    
    def __sort_by_date(self, releases : list[Release], reverse : bool = True) -> list[Release]:

        '''
            reverse = True => Descending
            reverse = False => Ascending
        '''

        lst : list[Release] = copy.deepcopy(releases)
        lst.sort(key = lambda release : release.date, reverse = reverse)

        return lst
    def __get_most_recent(self, releases : list[Release]) -> Tuple[str, datetime]:
        
        '''Returns (version, date).'''
        
        most_recent : Release = releases[0]

        return (most_recent.version, most_recent.date)

    @lru_cache(maxsize = 16)
    def fetch(self, package_name : str, only_final_releases : bool) -> Session:

        '''
            Retrieves all the releases from PyPi.org. 
            A "@lru_cache" with "maxsize = 16" is enabled on this method.
        '''

        url : str =  self.__format_url(package_name = package_name)
        response : Response = self.__get_function(url)
        xml_items_raw : list[XMLItem] = self.__parse_response(response = response)

        xml_items_clean : list[XMLItem] = copy.deepcopy(xml_items_raw)
        xml_items_clean = self.__filter(items = xml_items_clean, function = lambda x : self.__has_title(xml_item = x))
        xml_items_clean = self.__filter(items = xml_items_clean, function = lambda x : self.__has_pubdate(xml_item = x))
        
        releases : list[Release] = self.__convert_to_releases(package_name = package_name, xml_items = xml_items_clean)
        releases = self.__sort_by_date(releases = releases)

        if only_final_releases:
            releases = self.__filter(items = releases, function = lambda x : self.__is_final_release(release = x))        

        most_recent_version, most_recent_date = self.__get_most_recent(releases = releases)

        session : Session = Session(
            package_name = package_name,
            most_recent_version = most_recent_version,
            most_recent_date = most_recent_date,
            releases = releases,
            xml_items = xml_items_raw
        )

        return session
    
    def load_requirements(self, file_path : str) -> Tuple[list[Package], list[str]]:

        '''
            Expects a file_path to a "requirements.txt" file that looks like the following:

                requests >= 2.26.0
                asyncio == 3.4.3
                typed-astunparse >= 2.1.4, == 2.*
                dataclasses ~= 0.6
                opencv-python==4.10.0.84
                black==22.12.0
                certifi==2022.12.7
                ...

            Returns (packages, unparsed):

                packages = [
                    Package(name = "requests", version = "2.26.0"),
                    Package(name = "asyncio", version = "3.4.3"),
                    Package(name = "typed-astunparse", version = "2.1.4"),
                    Package(name = "dataclasses", version = "0.6"),
                    Package(name = "opencv-python", version = "4.10.0.84"),
                    Package(name = "black", version = "22.12.0")
                ]

                unparsed = [ 
                    "Some unparsable line."
                ]
        '''

        content : str = self.__file_reader_function(file_path)

        packages : list[Package] = []
        unparsed : list[str] = []

        for line in content.strip().splitlines():

            pattern : str = r'^([a-zA-Z0-9\-]+)[\s]*[>=<~]*\s*([\d\.]+)'
            match : Optional[Match] = re.match(pattern = pattern, string = line)

            if match:
                name, version = match.groups()
                package : Package = Package(name=name, version=version)
                packages.append(package)
            else:
                unparsed.append(line)

        return (packages, unparsed)
    def log_list(self, lst : list[Any]) -> None: 

        '''Adds a newline between each item of the provide lst before logging them.'''

        for item in lst:
            self.__logging_function(str(item))

# MAIN
if __name__ == "__main__":
    pass