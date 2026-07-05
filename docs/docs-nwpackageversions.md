# nwpackageversions
Contact: numbworks@gmail.com

## Revision History

| Date | Author | Description |
|---|---|---|
| 2024-10-07 | numbworks | Created. |
| 2026-07-05 | numbworks | Last update (2.0.1). |

## Introduction

`nwpackageversions` is a library that helps with retrieving package information from PyPi.org and comparing them with what you have installed locally.

## The XPath patterns

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

## Example files

1. [Dockerfile](ExampleFiles/Dockerfile)
2. [releases.xml](ExampleFiles/releases.xml)
3. [requirements.txt](ExampleFiles/requirements.txt)
4. [history.html](ExampleFiles/history.html)

## Known Issues: "Import nwpackageversions could not be resolved Pylance (reportMissingImports)"

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

## See Also: `asciibannermanager`

This project includes portions of the `asciibannermanager` project, which is documented here:

- [docs-asciibannermanager.md](SeeAlso-asciibannermanager/docs-asciibannermanager.md)

## See Also: `developerguide`

To get started with this project as a developer, please give a look to the following document:

- [docs-developerguide-python.md](SeeAlso-developerguide/docs-developerguide-python.md)

## See Also: `frameworkfreeze`

To learn more about the "framework freeze" strategy adopted by this project, please have a look at the following document:

- [docs-frameworkfreeze-python.md](SeeAlso-frameworkfreeze/docs-frameworkfreeze-python.md)

## See Also: `nwmakefiles`

This project includes portions of the `nwmakefiles` project, which is documented here:

- [docs-nwmakefiles.md](SeeAlso-nwmakefiles/docs-nwmakefiles.md)

## See Also: `nwbuilders`

This project includes portions of the `nwbuilders` project, which is documented here:

- [docs-nwbuilders-python.md](SeeAlso-nwbuilders/docs-nwbuilders-python.md)

## Legal Information

This software includes a RSS reader for PyPi.org. Due of the lack of a badge-related field in the RSS feed, which are necessary to discern stable releases from the others ("pre-release", "yanked"), a minimal web scraping functionality has been added in order to retrieve the badge from the release history page (```https://pypi.org/project/<package_name>/#history```).

At the moment of writing, the three legal pages related to PyPi.org do not prohibit web scraping:

- [Acceptable Use Policy](https://policies.python.org/pypi.org/Acceptable-Use-Policy/)
- [Code of Conduct](https://policies.python.org/pypi.org/Code-of-Conduct/)
- [Terms of Use](https://policies.python.org/pypi.org/Terms-of-Use/) 

For clarity, I am providing HTML snapshots as of today:

- [Acceptable Use Policy (August 8, 2024)](Legal/Acceptable_Use_Policy.html)
- [Code of Conduct (August 8, 2024)](Legal/Code_of_Conduct.html)
- [Terms of Use (July 2, 2024)](Legal/Terms_of_Use.html)

This functionality has been gracefully implemented, adopting a minimum `waiting_time` of five seconds for each GET request to not overload the servers, and it's disabled by default. 

The functionality is clearly explained in this documentation file, and users must actively enable it, assuming full responsibility for its fair use. The developer cannot be held responsible for any eventual improper use of this software.

## Markdown Toolset

Suggested toolset to view and edit this Markdown file:

- [Visual Studio Code](https://code.visualstudio.com/)
- [Markdown Preview Enhanced](https://marketplace.visualstudio.com/items?itemName=shd101wyy.markdown-preview-enhanced)
- [Markdown PDF](https://marketplace.visualstudio.com/items?itemName=yzane.markdown-pdf)