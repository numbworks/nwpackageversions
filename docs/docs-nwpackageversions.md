# nwpackageversions
Contact: numbworks@gmail.com

## Revision History

| Date | Author | Description |
|---|---|---|
| 2024-10-07 | numbworks | Created. |
| 2024-10-22 | numbworks | Updated to v1.1.0. |
| 2024-10-24 | numbworks | Updated to v1.2.0. |
| 2024-10-31 | numbworks | Updated to v1.6.0. |
| 2024-12-01 | numbworks | Updated to v1.8.0. |
| 2024-12-27 | numbworks | Updated to v1.8.1. |
| 2025-05-26 | numbworks | Updated to v1.8.2. |

## Introduction

`nwpackageversions` is a library that helps with retrieving package information from PyPi.org and comparing them with what you have installed locally.

## Getting Started

To run this application on Windows and Linux:

1. Download and install [Visual Studio Code](https://code.visualstudio.com/Download);
2. Download and install [Docker](https://www.docker.com/products/docker-desktop/);
3. Download and install [Git](https://git-scm.com/downloads);
4. Open your terminal application of choice and type the following commands:

    ```
    mkdir nwpackageversions
    cd nwpackageversions
    git clone https://github.com/numbworks/nwpackageversions.git
    ```

5. Launch Visual Studio Code and install the following extensions:

    - [Python](https://marketplace.visualstudio.com/items?itemName=ms-python.python)
    - [Pylance](https://marketplace.visualstudio.com/items?itemName=ms-python.vscode-pylance)
    - [Jupyter](https://marketplace.visualstudio.com/items?itemName=ms-toolsai.jupyter)
    - [Remote Development](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.vscode-remote-extensionpack)
    - [Docker](https://marketplace.visualstudio.com/items?itemName=ms-azuretools.vscode-docker)

6. In order for the Jupyter Notebook to automatically detect changes in the underlying library, click on <ins>File</ins> > <ins>Preferences</ins> > <ins>Settings</ins> and change the following setting as below:

    ```
    "jupyter.runStartupCommands": [
        "%load_ext autoreload", "%autoreload 2"
    ]
    ```

7. In order for Pylance to perform type checking, set the `python.analysis.typeCheckingMode` setting to `basic`;
8. Click on <ins>File</ins> > <ins>Open folder</ins> > `nwcommitaverages`;
9. Click on <ins>View</ins> > <ins>Command Palette</ins> and type:

    ```
    > Dev Container: Reopen in Container
    ```

10. Wait some minutes for the container defined in the <ins>.devcointainer</ins> folder to be built;
11. Done!

## Demo

The primary purpose of this Python library is to simplify and strengthen the process of keeping all project dependencies up-to-date.

An interactive demo environment for the scenario above is provided in the attached Jupyter Notebook file ([nwpackageversions.ipynb](../src/nwpackageversions.ipynb)).

## Unit Tests

To run the unit tests in Visual Studio Code (while still connected to the Dev Container):

1.  click on the <ins>Testing</ins> icon on the sidebar, right-click on <ins>tests</ins> > <ins>Run Test</ins>;
2. select the Python interpreter inside the Dev Container (if asked);
3. Done! 

To calculate the total unit test coverage in Visual Studio Code (while still connected to the Dev Container):

1. <ins>Terminal</ins> > <ins>New Terminal</ins>;
2. Run the following commands to get the total unit test coverage:

    ```
    cd tests
    coverage run -m unittest nwpackageversionstests.py
    coverage report --omit=nwpackageversionstests.py
    ```

3. Run the following commands to get the unit test coverage per class:

    ```
    cd tests
    coverage run -m unittest nwpackageversionstests.py
    coverage html --omit=nwpackageversionstests.py && sed -n '/<table class="index" data-sortable>/,/<\/table>/p' htmlcov/class_index.html | pandoc --from html --to plain && sleep 3 && rm -rf htmlcov
    ```

4. Done!

## The makefile

This software package ships with a `makefile` that include all the pre-release verification actions:

1. Launch Visual Studio Code;
2. Click on <ins>File</ins> > <ins>Open folder</ins> > `nwpackageversions`;
3. <ins>Terminal</ins> > <ins>New Terminal</ins>;
4. Run the following commands:

    ```
    cd /workspaces/nwpackageversions/scripts
    make -f makefile <target_name>
    ```
5. Done!

The avalaible target names are:

| Target Name | Description |
|---|---|
| type-verbose | Runs a type verification task and logs everything. |
| coverage-verbose | Runs a unit test coverage calculation task and logs the % per class. |
| tryinstall-verbose | Simulates a "pip install" and logs everything. |
| compile-verbose | Runs "python -m py_compile" command against the module file. |
| unittest-verbose | Runs "python" command against the test files. |
| codemetrics-verbose | Runs a cyclomatic complexity analysis against all the nw*.py files in /src. |
| update-codecoverage | Updates the codecoverage.txt/.svg files according to the total unit test coverage. |
| create-classdiagram | Creates a class diagram in Mermaid format that shows only relationships. |
| all-concise | Runs a batch of verification tasks and logs one summary line for each of them. |

The expected outcome for `all-concise` is:

```
MODULE_NAME: nwpackageversions
MODULE_VERSION: 1.8.2
COVERAGE_THRESHOLD: 70%
[OK] type-concise: passed!
[OK] changelog-concise: 'CHANGELOG' updated to current version!
[OK] setup-concise: 'setup.py' updated to current version!
[OK] coverage-concise: unit test coverage >= 70%.
[OK] tryinstall-concise: installation process works.
[OK] compile-concise: compiling the library throws no issues.
[OK] unittest-concise: '30' tests found and run.
[OK] codemetrics-concise: the cyclomatic complexity is excellent ('A').
```

Considering the old-fashioned syntax adopted by both `make` and `bash`, here a summary of its less intuitive aspects:

| Aspect | Description |
|---|---|
| `.PHONY` | All the targets that need to be called from another target need to be listed here. |
| `SHELL := /bin/bash` | By default, `make` uses `sh`, which doesn't support some functions such as string comparison. |
| `@` | By default, `make` logs all the commands included in the target. The `@` disables this behaviour. |
| `$$` | Necessary to escape `$`. |
| `$@` | Variable that stores the target name. |
| `if [[ ... ]]` | Double square brackets to enable pattern matching. |

## Known Issues - "Import nwpackageversions could not be resolved Pylance (reportMissingImports)"

If while trying to import `nwpackageversions` in `Visual Studio Code` the following warning appears:

```
Import nwpackageversions could not be resolved Pylance (reportMissingImports)
```

please:

1. in your terminal application of choice, launch the Python interpreter:

```powershell
PS C:\> python
```

2. run the following command:

```python
import nwpackageversions
print(nwpackageversions.__file__)
```

3. the console will output something like this:

```
C:\Users\Rubèn\src\nwpackageversions\src\nwpackageversions.py
```

4. open Visual Studio Code > <ins>File</ins> > <ins>Preferences</ins> > <ins>Settings</ins> and search for <ins>Python › Analysis: Extra Paths</ins>;

5. click on <ins>Add item</ins> and add the path above without the python file name: 

```
C:\Users\Rubèn\src\nwpackageversions\src\
```

6. restart Visual Studio Code;
7. Done!

## Appendix - The "label_pattern"

The `PyPiBadgeFetcher.try_fetch()` method adopts the following two XPath patterns:

```
version_pattern : str = "//p[@class='release__version'][span]/text()"
label_pattern : str = "//p[@class='release__version']/span[1]/text()"
```

The `[1]` ("take only the first span element") in the second pattern is necessary due of some packages having more than one badge per version - i.e [openpyxl](https://pypi.org/project/openpyxl/#history):

```
...
<p class="release__version">
   3.2.0b1
   <span class="badge badge--warning">pre-release</span>
   <span class="badge badge--danger">yanked</span>
</p>
<p class="release__version">
   2.6.0b1
   <span class="badge badge--warning">pre-release</span>
</p>
<p class="release__version">
   2.6.0a1
   <span class="badge badge--warning">pre-release</span>
</p>
...
```

## Appendix - Example files

1. [Dockerfile](ExampleFiles/Dockerfile)
2. [releases.xml](ExampleFiles/releases.xml)
3. [requirements.txt](ExampleFiles/requirements.txt)
4. [history.html](ExampleFiles/history.html)

## Disclaimer

This software includes a RSS reader for PyPi.org. Due of the lack of a badge-related field in the RSS feed, which are necessary to discern stable releases from the others ("pre-release", "yanked"), a minimal web scraping functionality has been added in order to retrieve the badge from the release history page (```https://pypi.org/project/<package_name>/#history```).

At the moment of writing, the three legal pages related to PyPi.org do not prohibit web scraping:

- [Acceptable Use Policy](https://policies.python.org/pypi.org/Acceptable-Use-Policy/)
- [Code of Conduct](https://policies.python.org/pypi.org/Code-of-Conduct/)
- [Terms of Use](https://policies.python.org/pypi.org/Terms-of-Use/) 

For clarity, I am providing HTML snapshots as of today:

- [Acceptable Use Policy (August 8, 2024)](Legal/Acceptable_Use_Policy.html)
- [Code of Conduct (August 8, 2024)](Legal/Code_of_Conduct.html)
- [Terms of Use (July 2, 2024)](Legal/Terms_of_Use.html)

This functionality has been gracefully implemented, adopting a minimum waiting_time of five seconds for each GET request to not overload the servers, and it's disabled by default. 

The functionality is clearly explained in this documentation file, and users must actively enable it, assuming full responsibility for its fair use. The developer cannot be held responsible for any eventual improper use of this software.

## Markdown Toolset

Suggested toolset to view and edit this Markdown file:

- [Visual Studio Code](https://code.visualstudio.com/)
- [Markdown Preview Enhanced](https://marketplace.visualstudio.com/items?itemName=shd101wyy.markdown-preview-enhanced)
- [Markdown PDF](https://marketplace.visualstudio.com/items?itemName=yzane.markdown-pdf)