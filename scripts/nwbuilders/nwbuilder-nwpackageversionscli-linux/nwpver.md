% nwpver

# NAME
nwpver - helps your Python project to stay up-to-date

# SYNOPSIS
**nwpver** [command] [options]

# DESCRIPTION
**nwpver** is a CLI application that helps with retrieving package information from PyPi.org and comparing them with what you have installed locally.

# COMMANDS

### runtime
Checks the status of the Python runtime.

**--required**
The required Python version (e.g., 3.12.5).

### requirements
Checks the status of the required packages.

**--file_path**
The path to the file containing package requirements.

**--only_stable_releases**
Whether to consider only stable releases or not.

**--waiting_time**
The waiting time between requests (in seconds).

# OPTIONS
**-h, --help**
Shows help and usage information.

# EXAMPLES

**Run it against the current runtime:**

```text
nwpver runtime --required 3.12.5
```

**Run it against a file_path:**

```text
nwpver requirements --file_path .devcontainer/main/Dockerfile --waiting_time 5
```

# PRE-REQUISITES
In order for *runtime* to work, Python must be installed on the machine.

# LEGAL INFORMATION
This software includes a RSS reader for PyPi.org. Due of the lack of a badge-related field in the RSS feed, which are necessary to discern stable releases from the others ("pre-release", "yanked"), a minimal web scraping functionality has been added in order to retrieve the badge from the release history page. At the moment of writing, the three legal pages related to PyPi.org do not prohibit web scraping. 

This functionality has been gracefully implemented, adopting a minimum `waiting_time` of five seconds for each GET request to not overload the servers, and it's disabled by default. The functionality is clearly explained in this documentation file, and users must actively enable it, assuming full responsibility for its fair use. The developer cannot be held responsible for any eventual improper use of this software.

# AUTHOR
numbworks (numbworks@gmail.com)