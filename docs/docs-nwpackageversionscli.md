# nwpackageversionscli
Contact: numbworks@gmail.com

## Revision History

| Date | Author | Description |
|---|---|---|
| 2026-04-11 | numbworks | Created. |
| 2026-04-11 | numbworks | Last update (2.0.0). |

## Introduction

`nwpackageversionscli` is a command-line application built on the top of `nwpackageversions`.

## CLI Reference

|Command|*Sub Command*|Options|Exit Codes|
|---|---|---|---|
|||*--help, -h*|Success|
|runtime||--required <br/>|Success<br/>Failure|
|requirements||--file_path <br/> *--only_stable_releases* <br/> *--waiting_time*|Success<br/>Failure|

|Option|Choices / Value|Default|
|---|---|---|
|--required|`<version>`|-|
|--file_paths|`<file path>`|-|
|*--only_stable_releases*|[`true`, `false`]|[`true`]|
|*--waiting_time*|`<seconds>`|[`15`]|

## Examples

Run it against the current runtime:

```sh
root@e584fefc57f0:/# alias nwpver="python src/nwpackageversionscli.py"
root@e584fefc57f0:/# nwpver runtime --required 3.12.5
```

```
*****************************************************************
'##::: ##:'##:::::'##:'########::'##::::'##:'########:'########::
 ###:: ##: ##:'##: ##: ##.... ##: ##:::: ##: ##.....:: ##.... ##:
 ####: ##: ##: ##: ##: ##:::: ##: ##:::: ##: ##::::::: ##:::: ##:
 ## ## ##: ##: ##: ##: ########:: ##:::: ##: ######::: ########::
 ##. ####: ##: ##: ##: ##.....:::. ##:: ##:: ##...:::: ##.. ##:::
 ##:. ###: ##: ##: ##: ##:::::::::. ## ##::: ##::::::: ##::. ##::
 ##::. ##:. ###. ###:: ##::::::::::. ###:::: ########: ##:::. ##:
..::::..:::...::...:::..::::::::::::...:::::........::..:::::..::
**********************************************Version: 2.0.0*****

command: 'runtime'
required: '(3, 12, 5)'

The installed Python version is matching the expected one (installed: '3.12.5', expected: '3.12.5').
```

Run it against a `file_path`:

```sh
root@e584fefc57f0:/# alias nwpver="python src/nwpackageversionscli.py"
root@e584fefc57f0:/# nwpver requirements --file_path .devcontainer/main/Dockerfile --waiting_time 5
```

```
*****************************************************************
'##::: ##:'##:::::'##:'########::'##::::'##:'########:'########::
 ###:: ##: ##:'##: ##: ##.... ##: ##:::: ##: ##.....:: ##.... ##:
 ####: ##: ##: ##: ##: ##:::: ##: ##:::: ##: ##::::::: ##:::: ##:
 ## ## ##: ##: ##: ##: ########:: ##:::: ##: ######::: ########::
 ##. ####: ##: ##: ##: ##.....:::. ##:: ##:: ##...:::: ##.. ##:::
 ##:. ###: ##: ##: ##: ##:::::::::. ## ##::: ##::::::: ##::. ##::
 ##::. ##:. ###. ###:: ##::::::::::. ###:::: ########: ##:::. ##:
..::::..:::...::...:::..::::::::::::...:::::........::..:::::..::
**********************************************Version: 2.0.0*****

command: 'requirements'
file_path: '.devcontainer/main/Dockerfile'
only_stable_releases: 'True'
waiting_time: '5'

total_packages: '9'
matching: '3'
matching_prc: '33.33%'
mismatching: '6'
mismatching_prc: '66.67%'

The current version ('2.32.3') of 'requests' doesn't match with the most recent release ('2.33.1', '2026-03-30').
The current version ('5.3.0') of 'lxml' doesn't match with the most recent release ('6.0.4', '2026-04-12').
The current version ('7.6.4') of 'coverage' doesn't match with the most recent release ('7.13.5', '2026-03-17').
The current version ('1.13.0') of 'mypy' doesn't match with the most recent release ('1.20.0', '2026-03-31').
The current version ('2.32.0.20241016') of 'types-requests' doesn't match with the most recent release ('2.33.0.20260408', '2026-04-08').
The current version ('3.3.3') of 'pylint' doesn't match with the most recent release ('4.0.5', '2026-02-20').
The current version ('0.9.0') of 'parameterized' matches with the most recent release ('0.9.0', '2023-03-27').
The current version ('0.5.1') of 'lxml-stubs' matches with the most recent release ('0.5.1', '2024-01-10').
The current version ('6.0.1') of 'radon' matches with the most recent release ('6.0.1', '2023-03-26').
```

## Markdown Toolset

Suggested toolset to view and edit this Markdown file:

- [Visual Studio Code](https://code.visualstudio.com/)
- [Markdown Preview Enhanced](https://marketplace.visualstudio.com/items?itemName=shd101wyy.markdown-preview-enhanced)
- [Markdown PDF](https://marketplace.visualstudio.com/items?itemName=yzane.markdown-pdf)