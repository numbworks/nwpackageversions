'''
A module that helps with retrieving package information from PyPi.org.

Alias: nwpv
'''

# GLOBAL MODULES
import copy
import os
import re
import requests
import sys
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from datetime import datetime
from lxml import html
from lxml.html import HtmlElement
from re import Match, Pattern
from requests import Response
from time import sleep
from typing import Any, Callable, Literal, Optional, Tuple, cast
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
class Badge():

    '''Represents a badge on PyPi.org.'''

    package_name : str
    version : str
    label : Literal["pre-release", "yanked"]

    def __str__(self):
        return str(
                "{ "
                f"'package_name': '{self.package_name}', "
                f"'version': '{self.version}', "
                f"'label': '{self.label}'"
                " }"                
            )
    def __repr__(self):
        return self.__str__()
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
    badges : Optional[list[Badge]]

    def __str__(self):

        mrr_formatter : Callable[[Release], str] = lambda mrr : f"('{mrr.version}', '{mrr.date.strftime("%Y-%m-%d")}')"
        badge_formatter : Callable[[Optional[list[Badge]]], str] = lambda badges : str(None) if badges is None else str(len(badges))

        return str(
                "{ "
                f"'package_name': '{self.package_name}', "
                f"'most_recent_release': '{mrr_formatter(self.most_recent_release)}', "
                f"'releases': '{len(self.releases)}', "
                f"'xml_items': '{len(self.xml_items)}', "
                f"'badges': '{badge_formatter(self.badges)}'"
                " }"                
            )
@dataclass(frozen = True)
class RequirementDetail():

    '''Represents a detailed requirement status.'''

    current_package : Package
    most_recent_release : Release
    is_version_matching : bool
    description : str

    def __str__(self):
        return str("{ " f"'description': '{self.description}'" " }")
    def __repr__(self):
        return self.__str__()
@dataclass(frozen = True)
class RequirementSummary():

    '''Represents a summarized requirement status.'''

    total_packages : int
    matching : int
    matching_prc : str
    mismatching : int
    mismatching_prc : str
    details : list[RequirementDetail]

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
    def __log_list(logging_function : Callable[[str], None], lst : list[Any]) -> None: 

        '''Adds a newline between each item of the provided lst before logging them.'''

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
    def list_logging_function() -> Callable[[Callable[[str], None], list[Any]], None]:

        '''
            An adapter around print() that adds a newline between each item of the provided lst before priting them.'''

        return lambda lf, lst : LambdaCollection.__log_list(lf, lst)
    @staticmethod
    def file_reader_function() -> Callable[[str], str]:

        '''An adapter around print().'''

        return lambda file_path : LambdaCollection.__load_content(file_path)    
    @staticmethod
    def sleeping_function() -> Callable[[int], None]:

        '''An adapter around time.sleep().'''

        return lambda waiting_time : sleep(cast(float, waiting_time))      
    @staticmethod
    def do_nothing_function() -> Callable[[Any], None]:

        '''Does nothing.'''

        return lambda x : None
class _MessageCollection():

    '''Collects all the messages used for logging and for the exceptions.'''

    @staticmethod
    def no_loading_strategy_found(file_path : str) -> str:
        return f"No loading strategy found for the provided file name. ('file_path': '{file_path}', 'supported_file_names' : [ 'requirements.txt', 'Dockerfile' ])"
    @staticmethod
    def no_packages_found(file_path : str) -> str:
        return f"No packages found in '{file_path}'. Please open the documentation to check the expected layout of the supported files."
    
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
    def total_estimated_time_will_be(waiting_time : int, local_packages : int) -> str:
        return f"The total estimated time to complete the whole operation will be: '{str(waiting_time * local_packages)}' seconds."       
    @staticmethod
    def status_evaluation_operation_successfully_loaded() -> str:
        return "The status evaluation operation has been successfully completed."
    @staticmethod
    def starting_creation_requirement_summary() -> str:
        return "Now starting the creation of a requirement summary..."
    @staticmethod
    def requirement_summary_successfully_created() -> str:
        return "The requirement summary has been successfully created."
    @staticmethod
    def status_checking_operation_completed() -> str:
        return "The status checking operation has been completed."       

    @staticmethod
    def no_suitable_xml_items_found(url : str) -> str:
        return f"No suitable XML items found in '{url}'. The application is not able to establish the most recent release."

    @staticmethod
    def __format_version(version : Tuple[int, int, int]) -> str:

        "Converts version to string."

        return f"{version[0]}.{version[1]}.{version[2]}"
    @staticmethod
    def installed_python_version_matching(installed : Tuple[int, int, int], required : Tuple[int, int, int]) -> str:
        installed_str : str = _MessageCollection.__format_version(version = installed)
        required_str : str = _MessageCollection.__format_version(version = required)
        return f"The installed Python version is matching the expected one (installed: '{installed_str}', expected: '{required_str}')."
    @staticmethod
    def installed_python_version_not_matching(installed : Tuple[int, int, int], required : Tuple[int, int, int]) -> str:
        installed_str : str = _MessageCollection.__format_version(version = installed)
        required_str : str = _MessageCollection.__format_version(version = required)
        return f"Warning! The installed Python is not matching the expected one (installed: '{installed_str}', expected: '{required_str}')."

# CLASSES
class LocalPackageLoader():

    '''This class collects all the logic related to load information about local packages.'''

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
    def __is_requirements(self, file_path : str) -> bool:

        '''
            Returns True if file_path contains a known file name for a requirements file.

            Examples:
                - r"C:/requirements.txt"
                - r"C:/requirements_175621.txt"
                - r"C:/requirements_demo.txt"
        '''

        if file_path.endswith("requirements.txt"):
            return True
        
        pattern : str = r".*\\requirements_.+\.txt$"
        if re.match(pattern, file_path.replace("/", "\\")):
            return True
        
        return False
    def __is_dockerfile(self, file_path : str) -> bool:

        '''
            Returns True if file_path contains a known file name for a Dockerfile file.

            Examples:
                - r"C:/Dockerfile"
                - r"C:/Dockerfile_175621"
                - r"C:/Dockerfile_demo"
        '''

        if file_path.endswith("Dockerfile"):
            return True
        
        pattern : str = r".*\\Dockerfile(_.+)?$"
        if re.match(pattern, file_path.replace("/", "\\")):
            return True
        
        return False
    def __load_from_requirements(self, file_path : str) -> LSession:

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
    def __load_from_dockerfile(self, file_path : str) -> LSession:

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

        '''
            It loads information about local packages from "requirements.txt" and "Dockerfile" files.

            Examples:

                - r"C:/requirements.txt"
                - r"C:/requirements_175621.txt"
                - r"C:/requirements_demo.txt"            
                - r"C:/Dockerfile"
                - r"C:/Dockerfile_175621"
                - r"C:/Dockerfile_demo"        
        '''

        l_session : Optional[LSession] = None

        if self.__is_requirements(file_path = file_path):
            l_session = self.__load_from_requirements(file_path = file_path)
        elif self.__is_dockerfile(file_path = file_path):
            l_session = self.__load_from_dockerfile(file_path = file_path)
        else:
            raise Exception(_MessageCollection.no_loading_strategy_found(file_path))
        
        if len(l_session.packages) == 0:
            raise Exception(_MessageCollection.no_packages_found(file_path))

        return cast(LSession, l_session)
class PyPiBadgeFetcher():

    '''This is an utility method to retrieve the badges associated to every release.'''

    __get_function : Callable[[str], Response]

    def __init__(
            self,
            get_function : Callable[[str], Response] = LambdaCollection.get_function()
            ) -> None:

        self.__get_function = get_function

    def __format_url(self, package_name : str) -> str:

        '''Returns the URL for the package's #history page.'''

        url : str =  f"https://pypi.org/project/{package_name}/#history"

        return url  
    def __extract_and_strip_text(self, tree : HtmlElement, pattern : str, remove_empty_items : bool = True) -> list[str]:

        '''
            Extracts strings from the provided tree using a XPath pattern that ends in "text()".
            
            Whitespaces, newlines and tabs are stripped out from each string.

            Optional: empty items are removed from the returned list.
        '''

        elements : list[HtmlElement] = tree.xpath(pattern)
        strs : list[str] = [element.strip() for element in elements]

        if remove_empty_items:
            strs = [str for str in strs if str]

        return strs
    def __create_badge(self, package_name : str, version : str, label : str) -> Badge:

        '''Creates a Badge object out of the provided arguments.'''

        badge : Badge = Badge(
            package_name = package_name, 
            version = version, 
            label = cast(Literal["pre-release", "yanked"], label)
        )

        return badge
    def __create_badges(self, package_name : str, versions_labels : list[Tuple[str, str]]) -> list[Badge]:

        '''Creates a list of Badge objects out of the provided arguments.'''

        badges : list[Badge] = []
        for tpl in versions_labels:
            badge : Badge = self.__create_badge(package_name = package_name, version = tpl[0], label = tpl[1])
            badges.append(badge)

        return badges

    def try_fetch(self, package_name : str) -> Optional[list[Badge]]:

        '''
            Fetches all the Badges for the provided package_name.

            If no badges are found, None is returned. 
        '''

        url : str = self.__format_url(package_name = package_name)
        
        response : Response = self.__get_function(url)
        tree : HtmlElement = html.fromstring(response.content)

        version_pattern : str = "//p[@class='release__version'][span]/text()"
        versions : list[str] = self.__extract_and_strip_text(tree = tree, pattern = version_pattern)

        if len(versions) == 0: 
            return None

        label_pattern : str = "//p[@class='release__version'][span]/span/text()"
        labels : list[str] = self.__extract_and_strip_text(tree = tree, pattern = label_pattern)

        versions_labels : list[Tuple[str, str]] = list(zip(versions, labels, strict = True))
        badges : list[Badge] = self.__create_badges(package_name = package_name, versions_labels = versions_labels)

        return badges
class PyPiReleaseFetcher():

    '''This is a client for PyPi release pages.'''

    __get_function : Callable[[str], Response]
    __badge_fetcher : PyPiBadgeFetcher

    def __init__(
            self,
            get_function : Callable[[str], Response] = LambdaCollection.get_function(),
            badge_fetcher : PyPiBadgeFetcher = PyPiBadgeFetcher()
            ) -> None:

        self.__get_function = get_function
        self.__badge_fetcher = badge_fetcher

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

        '''Retuns False if xml_item.title is None.'''

        if xml_item.title:
            return True
        else:
            return False
    def __has_pubdate(self, xml_item : XMLItem) -> bool:

        '''Retuns False if xml_item.pubdate is None.'''

        if xml_item.pubdate:
            return True
        else:
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

    def __is_stable_release(self, xml_item : XMLItem, badge_versions : list[str]) -> bool:

        '''
            (xml_item.title not in badge_versions) == True => stable
            (xml_item.title not in badge_versions) == False => unstable
        '''

        return (xml_item.title not in badge_versions)
    def __process_stable_releases(self, package_name : str, xml_items_clean : list[XMLItem], only_stable_releases : bool) -> Tuple[list[XMLItem], Optional[list[Badge]]]:

        '''Encapsulates all the logic related to stable releases.'''

        badges : Optional[list[Badge]] = None

        if only_stable_releases == False:
            return (xml_items_clean, badges)
        
        badges = self.__badge_fetcher.try_fetch(package_name = package_name)       
        
        if badges is None:
            return (xml_items_clean, badges)

        badge_versions : list[str] = [badge.version for badge in badges]
        xml_items_clean = self.__filter(
            items = xml_items_clean, 
            function = lambda x : self.__is_stable_release(xml_item = x, badge_versions = badge_versions)
        )

        return (xml_items_clean, badges)

    def fetch(self, package_name : str, only_stable_releases : bool) -> FSession:

        '''
            Retrieves all the releases from PyPi.org for the provided package_name.
            
            The "only_stable_releases" flag, if True, will filter out all the releases that have been badged as "pre-release" or "yanked".
        '''

        url : str =  self.__format_url(package_name = package_name)
        response : Response = self.__get_function(url)
        xml_items_raw : list[XMLItem] = self.__parse_response(response = response)

        xml_items_clean : list[XMLItem] = copy.deepcopy(xml_items_raw)
        xml_items_clean = self.__filter(items = xml_items_clean, function = lambda x : self.__has_title(xml_item = x))
        xml_items_clean = self.__filter(items = xml_items_clean, function = lambda x : self.__has_pubdate(xml_item = x))
        xml_items_clean, badges = self.__process_stable_releases(package_name = package_name, xml_items_clean = xml_items_clean, only_stable_releases = only_stable_releases)
            
        if len(xml_items_clean) == 0:
            raise Exception(_MessageCollection.no_suitable_xml_items_found(url = url))

        releases : list[Release] = self.__convert_to_releases(package_name = package_name, xml_items = xml_items_clean)
        releases = self.__sort_by_date(releases = releases)

        f_session : FSession = FSession(
            package_name = package_name,
            most_recent_release = self.__get_most_recent(releases = releases),
            releases = releases,
            xml_items = xml_items_raw,
            badges = badges
        )

        return f_session
class RequirementChecker():

    '''This class collects all the logic related to requirement status checking.'''

    __package_loader : LocalPackageLoader
    __release_fetcher : PyPiReleaseFetcher
    __logging_function : Callable[[str], None]
    __list_logging_function : Callable[[Callable[[str], None], list[Any]], None]
    __sleeping_function : Callable[[int], None]

    def __init__(
            self, 
            package_loader : LocalPackageLoader = LocalPackageLoader(),
            release_fetcher : PyPiReleaseFetcher = PyPiReleaseFetcher(),
            logging_function : Callable[[str], None] = LambdaCollection.logging_function(),
            list_logging_function : Callable[[Callable[[str], None], list[Any]], None] = LambdaCollection.list_logging_function(),
            sleeping_function : Callable[[int], None] = LambdaCollection.sleeping_function()
            ) -> None:
      
        self.__package_loader = package_loader
        self.__release_fetcher = release_fetcher
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
    def __create_requirement_detail(self, current_package : Package, most_recent_release : Release) -> RequirementDetail:

        '''Creates a RequirementDetail object out of the provided current_package and most_recent_release.'''

        is_version_matching, description = self.__compare(
            current_package = current_package, 
            most_recent_release = most_recent_release
        )

        requirement_detail : RequirementDetail = RequirementDetail(
            current_package = current_package,
            most_recent_release = most_recent_release,
            is_version_matching = is_version_matching,
            description = description
        )

        return requirement_detail
    def __create_requirement_details(self, l_session : LSession, waiting_time : int) -> list[RequirementDetail]:

        '''Creates a list of RequirementDetail objects out of the provided l_session.'''

        requirement_details : list[RequirementDetail] = []
        for current_package in l_session.packages:

            f_session : FSession = self.__release_fetcher.fetch(package_name = current_package.name)
            
            requirement_detail : RequirementDetail = self.__create_requirement_detail(
                current_package = current_package, 
                most_recent_release = f_session.most_recent_release
            )
            requirement_details.append(requirement_detail)

            self.__sleeping_function(waiting_time)
        
        return requirement_details
    def __calculate_prc(self, value : int, total : int) -> str:

        '''Calculates % out of provided value and total.'''

        prc : str = f"{(value / total) * 100:.2f}%"

        return prc
    def __create_requirement_summary(self, requirement_details : list[RequirementDetail]) -> RequirementSummary:

        '''Creates a RequirementSummary object out of the provided requirement_details.'''

        total_packages : int = len(requirement_details)
        matching : int = 0
        mismatching : int = 0

        for requirement_detail in requirement_details:
            
            if requirement_detail.is_version_matching == True:
                matching += 1
            else:
                mismatching += 1

        requirement_summary : RequirementSummary = RequirementSummary(
            total_packages = total_packages,
            matching = matching,
            matching_prc = self.__calculate_prc(value = matching, total = total_packages),
            mismatching = mismatching,
            mismatching_prc = self.__calculate_prc(value = mismatching, total = total_packages),
            details = requirement_details
        )

        return requirement_summary

    def check(self, file_path : str, waiting_time : int = 5) -> RequirementSummary:

        '''
            This method:
            
                1. loads a list of locally-installed Python packages from file_path
                2. fetches the latest information about each of them on PyPi.org
                3. returns a RequirementSummary object
            
            All the steps are logged.
            It raises an Exception if an issue arises.
        '''

        minimum_wt : int = 5
        if waiting_time < minimum_wt:
            raise Exception(_MessageCollection.waiting_time_cant_be_less_than(waiting_time, minimum_wt))

        self.__logging_function(_MessageCollection.status_checking_operation_started())
        self.__logging_function(_MessageCollection.list_local_packages_will_be_loaded(file_path))
        self.__logging_function(_MessageCollection.waiting_time_will_be(waiting_time))

        l_session : LSession = self.__package_loader.load(file_path = file_path)

        self.__logging_function(_MessageCollection.x_local_packages_found_successfully_loaded(l_session.packages))
        self.__logging_function(_MessageCollection.x_unparsed_lines(l_session.unparsed_lines))
        self.__logging_function(_MessageCollection.starting_to_evaluate_status_local_package())
        self.__logging_function(_MessageCollection.total_estimated_time_will_be(waiting_time, len(l_session.packages)))
        
        requirement_details : list[RequirementDetail] = self.__create_requirement_details(l_session = l_session, waiting_time = waiting_time)

        self.__logging_function(_MessageCollection.status_evaluation_operation_successfully_loaded())
        self.__list_logging_function(self.__logging_function, requirement_details)
        self.__logging_function(_MessageCollection.starting_creation_requirement_summary())

        requirement_summary : RequirementSummary = self.__create_requirement_summary(requirement_details = requirement_details)

        self.__logging_function(_MessageCollection.requirement_summary_successfully_created())
        self.__logging_function(str(requirement_summary))
        self.__logging_function(_MessageCollection.status_checking_operation_completed())

        return requirement_summary
    def try_check(self, file_path : str, waiting_time : int = 5) -> Optional[RequirementSummary]:

        '''
            It performs the same operations as check().
            It doesn't raise an Exception if an issue arises, but it logs it and returns None.
        '''

        try:
            
            return self.check(file_path = file_path, waiting_time = waiting_time)

        except Exception as e:

            self.__logging_function(str(e))
            
            return None
    def log_requirement_summary(self, requirement_summary : RequirementSummary) -> None:

        '''Logs requirement_summary by using logging_function and list_logging_function.'''

        self.__logging_function(str(requirement_summary))
        self.__list_logging_function(self.__logging_function, requirement_summary.details)
    def get_default_devcointainer_dockerfile_path(self) -> str:
        
        '''
            This assumes that:

                - the *.py file from which the consumer is calling this method is stored into <root>/src;
                - the Dockerfile is placed into <root>/.devcontainer folder instead.

            Example:

                os.path.join(os.path.abspath(os.curdir).replace("src", ".devcontainer"), "Dockerfile")
        '''
        
        dockerfile_path : str = os.path.join(
            os.path.abspath(os.curdir).replace("src", ".devcontainer"), 
            "Dockerfile"
        )

        return dockerfile_path
class LanguageChecker():

    '''Collects all the logic related to Python language checks.'''

    def get_version_status(self, required : Tuple[int, int, int] = (3, 12, 1)) -> str:

        '''Returns a warning message if the installed Python version doesn't match the required one.'''

        installed : Tuple[int, int, int] = (sys.version_info.major, sys.version_info.minor, sys.version_info.micro)
        
        if installed == required:
            return _MessageCollection.installed_python_version_matching(installed = installed, required = required)
        else:
            return _MessageCollection.installed_python_version_not_matching(installed = installed, required = required)
        
# MAIN
if __name__ == "__main__":
    fsession = PyPiReleaseFetcher().fetch(package_name = "ipykernel", only_stable_releases = True)
    print(fsession)