'''
A module that helps with retrieving package information from PyPi.org.

Alias: nwpv
'''

# GLOBAL MODULES
import copy
import re
from time import sleep
import requests
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from datetime import datetime
from functools import lru_cache
from re import Match, Pattern
from requests import Response
from typing import Any, Callable, Optional, Tuple, cast
from xml.etree.ElementTree import Element

# LOCAL MODULES
# CONSTANTS
# DTOs
@dataclass(frozen = True)
class Package():

    '''Represents an installed package.'''

    name : str
    version : str
@dataclass(frozen = True)
class LSession():

    '''Represents a loading session.'''

    packages : list[Package]
    unparsed_lines : list[str]

    def __str__(self):
        return str(
                "{ "
                f"'packages': '{len(self.packages)}', "
                f"'unparsed_lines': '{len(self.unparsed_lines)}'"
                " }"                
            )  
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
class FSession():

    '''Represents a fetching session.'''

    package_name : str
    most_recent_release : Release
    releases : list[Release]
    xml_items : list[XMLItem]

    def __str__(self):

        mrr_formatter : Callable[[Release], str] = lambda mrr : f"('{mrr.version}', '{mrr.date.strftime("%Y-%m-%d")}')"

        return str(
                "{ "
                f"'package_name': '{self.package_name}', "
                f"'most_recent_release': '('{self.most_recent_release.version}', '{self.most_recent_release.date.strftime("%Y-%m-%d")}')', "
                f"'releases': '{len(self.releases)}', "
                f"'xml_items': '{len(self.xml_items)}'"
                " }"                
            )   
@dataclass(frozen = True)
class StatusDetail():

    '''Represents a detailed status.'''

    current_package : Package
    most_recent_release : Release
    is_version_matching : bool
    description : str

    def __str__(self):
        return str("{ " f"'description': '{self.description}'" " }")
    def __repr__(self):
        return self.__str__()
@dataclass(frozen = True)
class StatusSummary():

    '''Represents a summarized status.'''

    total_packages : int
    matching : int
    matching_prc : str
    mismatching : int
    mismatching_prc : str
    details : list[StatusDetail]

    def __str__(self):
        return str(
                "{ "
                f"'total_packages': '{str(self.total_packages)}', "
                f"'matching': '{str(self.matching)}', "
                f"'matching_prc': '{self.matching_prc}', "
                f"'mismatching': '{str(self.mismatching)}', "
                f"'mismatching_prc': '{self.mismatching_prc}'"
                " }"                
            )  

# STATIC CLASSES
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
    def __log_list(lst : list[Any]) -> None: 

        '''Adds a newline between each item of the provided lst before logging them.'''

        logging_function : Callable[[str], None] = LambdaCollection.logging_function()

        for item in lst:
            logging_function(str(item))

    @staticmethod
    def get_function() -> Callable[[str], Response]:

        '''An adapter around requests.get(url).'''

        return lambda url : requests.get(url)
    @staticmethod
    def logging_function() -> Callable[[str], None]:

        '''An adapter around print().'''

        return lambda msg : print(msg)
    @staticmethod
    def list_logging_function() -> Callable[[list[Any]], None]:

        '''
            An adapter around print() that adds a newline between each item of the provided lst before priting them.'''

        return lambda lst : LambdaCollection.__log_list(lst)   
    @staticmethod
    def file_reader_function() -> Callable[[str], str]:

        '''An adapter around print().'''

        return lambda file_path : LambdaCollection.__load_content(file_path)    
    @staticmethod
    def sleeping_function() -> Callable[[int], None]:

        '''An adapter around time.sleep().'''

        return lambda waiting_time : sleep(cast(float, waiting_time))      
class _MessageCollection():

    '''Collects all the messages used for logging and for the exceptions.'''

    @staticmethod
    def no_loading_strategy_found(file_path : str) -> str:
        return f"No loading strategy found for the provided file name. ('file_path': '{file_path}', 'supported_file_names' : [ 'requirements.txt', 'Dockerfile' ])"
    @staticmethod
    def zero_packages_found(file_path : str) -> str:
        return f"Zero packages found in '{file_path}'. Please open the documentation to check the expected layout of the supported files."
    
    @staticmethod
    def waiting_time_cant_be_less_than(waiting_time : int, expected : int) -> str:
        return f"Waiting time ('{str(waiting_time)}') can't be less than {expected} seconds."
    @staticmethod
    def current_version_matches(current_package : Package, most_recent_release : Release) -> str:
        return f"The current version ('{current_package.version}') of '{current_package.name}' matches with the most recent release ('{most_recent_release.version}', '{most_recent_release.date.strftime("%Y-%m-%d")}')."
    @staticmethod
    def current_version_doesnt_match(current_package : Package, most_recent_release : Release) -> str:
        return f"The current version ('{current_package.version}') of '{current_package.name}' doesn't match with the most recent release ('{most_recent_release.version}', '{most_recent_release.date.strftime("%Y-%m-%d")}')."
    @staticmethod
    def status_checking_operation_started() -> str:
        return "The status checking operation has started!"
    @staticmethod
    def list_local_packages_will_be_loaded(file_path : str) -> str:
        return f"The list of local packages will be loaded from the following 'file_path': '{file_path}'."
    @staticmethod
    def waiting_time_will_be(waiting_time : int) -> str:
        return f"The 'waiting_time' between each fetching request will be: '{str(waiting_time)}' seconds."
    @staticmethod
    def x_local_packages_found_successfully_loaded(packages : list[Package]) -> str:
        return f"'{str(len(packages))}' local packages has been found and successfully loaded."        
    @staticmethod
    def x_unparsed_lines(unparsed_lines : list[str]) -> str:
        
        msg : str = f"'{str(len(unparsed_lines))}' unparsed lines."

        if len(unparsed_lines) > 0:
            msg += "\n"
            msg += "These are: "
            msg += str(unparsed_lines)
        
        return msg
    @staticmethod
    def starting_to_evaluate_status_local_package() -> str:
        return "Now starting to evaluate the status of each local package..."
    @staticmethod
    def status_evaluation_operation_successfully_loaded() -> str:
        return "The status evaluation operation has been successfully completed."
    @staticmethod
    def starting_creation_status_summary() -> str:
        return "Now starting the creation of a status summary..."
    @staticmethod
    def status_summary_successfully_created() -> str:
        return "The status summary has been successfully created."
    @staticmethod
    def status_checking_operation_completed() -> str:
        return "The status checking operation has been completed."       

# CLASSES
class LocalPackageManager():

    '''This class collects all the logic related to local package management.'''

    __file_reader_function : Callable[[str], str]

    def __init__(
            self, 
            file_reader_function : Callable[[str], str] = LambdaCollection.file_reader_function()
            ) -> None:

        self.__file_reader_function = file_reader_function

    def __clean_unparsed_lines(self, unparsed_lines : list[str]) -> list[str] :

        '''Removes empty strings from unparsed_lines.'''

        unparsed_lines = [line for line in unparsed_lines if line]

        return unparsed_lines

    def load_from_requirements(self, file_path : str) -> LSession:

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

            Returns a LSession:

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
        pattern : str = r'^([a-zA-Z0-9\-]+)[\s]*[>=<~]*\s*([\d\.]+)'

        packages : list[Package] = []
        unparsed_lines : list[str] = []

        for line in content.strip().splitlines():

            match : Optional[Match] = re.match(pattern = pattern, string = line)

            if match:
                name, version = match.groups()
                package : Package = Package(name=name, version=version)
                packages.append(package)
            else:
                unparsed_lines.append(line)

        unparsed_lines = self.__clean_unparsed_lines(unparsed_lines = unparsed_lines)

        l_session : LSession = LSession(
            packages = packages,
            unparsed_lines = unparsed_lines
        )

        return l_session
    def load_from_dockerfile(self, file_path : str) -> LSession:

        '''
            Expects a file_path to a "Dockerfile" file that looks like the following:

                FROM python:3.12.5-bookworm

                RUN pip install requests==2.26.0
                RUN pip install beautifulsoup4==4.10.0
                ...

            Returns a LSession:

                packages = [
                    Package(name = "requests", version = "2.26.0"),
                    Package(name = "beautifulsoup4", version = "4.10.0"),
                    ...
                ]

                unparsed = [ 
                    "Some unparsable line."
                ]
        '''

        content : str = self.__file_reader_function(file_path)
        pattern : Pattern = re.compile(r"pip install ([\w\-\_]+)(==)([\d\.]+)")

        packages : list[Package] = []
        unparsed_lines : list[str] = []

        for line in content.strip().splitlines():

            match : Optional[Match] = pattern.search(string = line)

            if match:
                package : Package = Package(name = match.group(1), version = match.group(3))
                packages.append(package)
            else:
                unparsed_lines.append(line)

        unparsed_lines = self.__clean_unparsed_lines(unparsed_lines = unparsed_lines)

        l_session : LSession = LSession(
            packages = packages,
            unparsed_lines = unparsed_lines
        )

        return l_session
    def load(self, file_path : str) -> LSession:

        '''It supports two files: "requirements.txt" and "Dockerfile"'''

        l_session : Optional[LSession] = None

        if file_path.endswith("requirements.txt"):
            l_session = self.load_from_requirements(file_path = file_path)
        elif file_path.endswith("Dockerfile"):
            l_session = self.load_from_dockerfile(file_path = file_path)
        else:
            raise Exception(_MessageCollection.no_loading_strategy_found(file_path))
        
        if l_session.packages == 0:
            raise Exception(_MessageCollection.zero_packages_found(file_path))

        return cast(LSession, l_session)
class PyPiReleaseManager():

    '''This is a client for PyPi release pages.'''

    __get_function : Callable[[str], Response]

    def __init__(
            self,
            get_function : Callable[[str], Response] = LambdaCollection.get_function()
            ) -> None:

        self.__get_function = get_function

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
    def __sort_by_date(self, releases : list[Release], reverse : bool = True) -> list[Release]:

        '''
            reverse = True => Descending
            reverse = False => Ascending
        '''

        lst : list[Release] = copy.deepcopy(releases)
        lst.sort(key = lambda release : release.date, reverse = reverse)

        return lst
    def __get_most_recent(self, releases : list[Release]) -> Release:
        
        '''Returns most_recent_release by assuming releases are sorted in descending order.'''
        
        most_recent_release : Release = releases[0]

        return most_recent_release

    @lru_cache(maxsize = 16)
    def fetch(self, package_name : str) -> FSession:

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

        f_session : FSession = FSession(
            package_name = package_name,
            most_recent_release = self.__get_most_recent(releases = releases),
            releases = releases,
            xml_items = xml_items_raw
        )

        return f_session
class StatusChecker():

    '''This class collects all the logic related to package status checking.'''

    __package_manager : LocalPackageManager
    __release_manager : PyPiReleaseManager
    __logging_function : Callable[[str], None]
    __list_logging_function : Callable[[list[Any]], None]
    __sleeping_function : Callable[[int], None]

    def __init__(
            self, 
            package_manager : LocalPackageManager = LocalPackageManager(),
            release_manager : PyPiReleaseManager = PyPiReleaseManager(),
            logging_function : Callable[[str], None] = LambdaCollection.logging_function(),
            list_logging_function : Callable[[list[Any]], None] = LambdaCollection.list_logging_function(),
            sleeping_function : Callable[[int], None] = LambdaCollection.sleeping_function()
            ) -> None:
      
        self.__package_manager = package_manager
        self.__release_manager = release_manager
        self.__logging_function = logging_function
        self.__list_logging_function = list_logging_function
        self.__sleeping_function = sleeping_function

    def __compare(self, current_package : Package, most_recent_release : Release) -> Tuple[bool, str]:

        '''Returns (is_version_matching, description).'''

        is_version_matching : Optional[bool] = None        
        description : Optional[str] = None

        if current_package.version == most_recent_release.version:
            is_version_matching = True
            description = _MessageCollection.current_version_matches(current_package, most_recent_release)
        else:
            is_version_matching = False
            description = _MessageCollection.current_version_doesnt_match(current_package, most_recent_release)

        return (cast(bool, is_version_matching), cast(str, description))
    def __create_status_detail(self, current_package : Package, most_recent_release : Release) -> StatusDetail:

        '''Creates a StatusDetail object out of the provided current_package and most_recent_release.'''

        is_version_matching, description = self.__compare(
            current_package = current_package, 
            most_recent_release = most_recent_release
        )

        status_detail : StatusDetail = StatusDetail(
            current_package = current_package,
            most_recent_release = most_recent_release,
            is_version_matching = is_version_matching,
            description = description
        )

        return status_detail
    def __create_status_details(self, l_session : LSession, waiting_time : int) -> list[StatusDetail]:

        '''Creates a list of StatusDetail objects out of the provided l_session.'''

        status_details : list[StatusDetail] = []
        for current_package in l_session.packages:

            f_session : FSession = self.__release_manager.fetch(package_name = current_package.name)
            
            status_detail : StatusDetail = self.__create_status_detail(
                current_package = current_package, 
                most_recent_release = f_session.most_recent_release
            )
            status_details.append(status_detail)

            self.__sleeping_function(waiting_time)
        
        return status_details
    def __calculate_prc(self, value: int, total : int) -> str:

        '''Calculates % out of provided value and total.'''

        prc : str = f"{(value / total) * 100:.2f}%"

        return prc
    def __create_status_summary(self, status_details : list[StatusDetail]) -> StatusSummary:

        '''Creates a StatusSummary object out of the provided status_details.'''

        total_packages : int = len(status_details)
        matching : int = 0
        mismatching : int = 0

        for status_detail in status_details:
            
            if status_detail.is_version_matching == True:
                matching += 1
            else:
                mismatching += 1

        status_summary : StatusSummary = StatusSummary(
            total_packages = total_packages,
            matching = matching,
            matching_prc = self.__calculate_prc(value = matching, total = total_packages),
            mismatching = mismatching,
            mismatching_prc = self.__calculate_prc(value = mismatching, total = total_packages),
            details = status_details
        )

        return status_summary

    def check(self, file_path : str, waiting_time : int = 5) -> StatusSummary:

        '''
            This method:
            
                1. loads a list of locally-installed Python packages from file_path
                2. fetches the latest information about each of them on PyPi.org
                3. returns a StatusSummary object
            
            All the steps are logged.
            It raises an Exception if an issue arises.
        '''

        minimum_wt : int = 5
        if waiting_time < minimum_wt:
            raise Exception(_MessageCollection.waiting_time_cant_be_less_than(waiting_time, minimum_wt))

        self.__logging_function(_MessageCollection.status_checking_operation_started())
        self.__logging_function(_MessageCollection.list_local_packages_will_be_loaded(file_path))
        self.__logging_function(_MessageCollection.waiting_time_will_be(waiting_time))

        l_session : LSession = self.__package_manager.load(file_path = file_path)

        self.__logging_function(_MessageCollection.x_local_packages_found_successfully_loaded(l_session.packages))
        self.__logging_function(_MessageCollection.x_unparsed_lines(l_session.unparsed_lines))
        self.__logging_function(_MessageCollection.starting_to_evaluate_status_local_package())

        status_details : list[StatusDetail] = self.__create_status_details(l_session = l_session, waiting_time = waiting_time)

        self.__logging_function(_MessageCollection.status_evaluation_operation_successfully_loaded())
        self.__list_logging_function(status_details)
        self.__logging_function(_MessageCollection.starting_creation_status_summary())

        status_summary : StatusSummary = self.__create_status_summary(status_details = status_details)

        self.__logging_function(_MessageCollection.status_summary_successfully_created())
        self.__logging_function(str(status_summary))
        self.__logging_function(_MessageCollection.status_checking_operation_completed())

        return status_summary
    def try_check(self, file_path : str, waiting_time : int = 5) -> Optional[StatusSummary]:

        '''
            It performs the same operations as check().
            It doesn't raise an Exception if an issue arises, but it logs it and returns None.
        '''

        try:
            
            return self.check(file_path = file_path, waiting_time = waiting_time)

        except Exception as e:

            self.__logging_function(str(e))
            
            return None
    def log_status_summary(self, status_summary : StatusSummary) -> None:

        '''Logs status_summary by using logging_function and list_logging_function.'''

        self.__logging_function(str(status_summary))
        self.__list_logging_function(status_summary.details)

# MAIN
if __name__ == "__main__":
    pass