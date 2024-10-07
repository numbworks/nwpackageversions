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
from requests import Response
from typing import Callable, Optional, Tuple, cast
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
@dataclass(frozen = True)
class Release():

    '''Represents a release on PyPi.org. It's a subset of XMLItem.'''

    package_name : str
    version : str
    date : datetime
@dataclass(frozen = True)
class Session():

    '''Represents a fetching session performed by PyPiReleaseManager.'''

    package_name : str
    latest_version : Optional[str]
    latest_version_date : Optional[datetime]
    releases : list[Release]
    xml_items : list[XMLItem]

# STATIC CLASSES
# CLASSES
class PyPiReleaseManager():

    '''This is a client for PyPi release pages.'''

    __get_function : Callable[[str], Response]
    __logging_function : Callable[[str], None]

    def __init__(
            self, 
            get_function : Callable[[str], Response] = lambda url : requests.get(url),
            logging_function : Callable[[str], None] = lambda msg : print(msg)) -> None:
        
        self.__get_function = get_function
        self.__logging_function = logging_function

    def __format_url(self, package_name : str) -> str:

        '''Returns the URL for the package's releases.xml.'''

        url : str =  f"https://pypi.org/rss/project/{package_name}/releases.xml"

        return url
    def __format_optional_string(self, opt : Optional[str]) -> str:

        '''Returns "string" or "None".'''

        string : str = "None"
        if opt is not None:
            string = str(opt)

        return string
    def __format_optional_datetime(self, dt : Optional[datetime]) -> str:

        '''Returns a date string formatted as "2024-10-05" or "None".'''

        dt_str : str = "None"
        if dt is not None:
            dt_str = cast(datetime, dt).strftime('%Y-%m-%d')

        return dt_str      
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
    def __is_final_release(self, xml_item : XMLItem) -> bool:

        '''
            ['2.1.2', '2.1.1', '2.0.2', '2.1.0']    => True
            ['2.1.0rc1', '7.0.0b1']                 => False
        '''

        pattern : str = r'^\d+\.\d+\.\d+$'
        status : bool = bool(re.match(pattern, str(xml_item.title)))

        return status
    def __filter(self, xml_items : list[XMLItem], function : Callable[[XMLItem], bool]) -> list[XMLItem]:

        '''Runs function on releases.'''

        lst : list[XMLItem] = [xml_item for xml_item in xml_items if function(xml_item)]

        return lst
    def __sort_by_pubdate(self, xml_items : list[XMLItem], reverse : bool = True) -> list[XMLItem]:

        '''
            reverse = True => Descending
            reverse = False => Ascending
        '''

        lst : list[XMLItem] = copy.deepcopy(xml_items)
        lst.sort(key = lambda x : cast(datetime, x.pubdate), reverse = reverse)

        return lst
    def __get_most_recent(self, xml_items : list[XMLItem]) -> Tuple[Optional[str], Optional[datetime]]:
        
        '''Returns (title, pubdate).'''
        
        most_recent : XMLItem = xml_items[0]
        if most_recent is None:
            return (None, None)

        return (xml_items[0].title, xml_items[0].pubdate)
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

    def fetch(self, package_name : str, only_final_releases : bool) -> Session:

        '''Retrieves all the releases from PyPi.org.'''

        url : str =  self.__format_url(package_name = package_name)
        response : Response = self.__get_function(url)

        xml_items : list[XMLItem] = self.__parse_response(response = response)
        xml_items = self.__filter(xml_items = xml_items, function = lambda x : self.__has_title(xml_item = x))
        xml_items = self.__filter(xml_items = xml_items, function = lambda x : self.__has_pubdate(xml_item = x))
        xml_items = self.__sort_by_pubdate(xml_items = xml_items)

        if only_final_releases:
            xml_items = self.__filter(xml_items = xml_items, function = lambda x : self.__is_final_release(xml_item = x))

        latest_version, latest_version_date = self.__get_most_recent(xml_items = xml_items)

        session : Session = Session(
            package_name = package_name,
            xml_items = xml_items,
            latest_version = latest_version,
            latest_version_date = latest_version_date
        )

        return session
    def format_session(self, session : Session) -> str:

        '''
            Formats the content of the provided session.

            Example: "('numpy', '2.1.2', '2024-10-05')"    
        '''

        latest_version : str = self.__format_optional_string(opt = session.latest_version)
        latest_version_date_str : str = self.__format_optional_datetime(dt = session.latest_version_date)

        msg : str = f"('{session.package_name}', '{latest_version}', '{latest_version_date_str}')"

        return msg       
    def format_xml_item(self, xml_item : XMLItem) -> str:

        '''
            Formats the content of the provided release.

            Example: "{ 'title': '2.1.2', 'pubdate': '2024-10-05' }"
        '''

        return str(
                "{ "
                f"'title': '{xml_item.title}', "
                f"'pubdate': '{self.__format_optional_datetime(dt = xml_item.pubdate)}'"
                " }"                
            ) 
    def log_session(self, session : Session) -> None:

        '''Formats the content of the provided session and logs it.'''

        msg : str = self.format_session(session = session)
        self.__logging_function(msg)
    def log_releases(self, xml_releases : list[XMLItem]) -> None: 

        '''Logs releases.'''

        for release in xml_releases:
            msg : str = self.format_xml_item(xml_item = release)
            self.__logging_function(msg)

# MAIN
if __name__ == "__main__":
    pass