# <a href="https://botstrap.rtfd.io"><img src="/docs/images/logo-48.png" width=24></a> Library Examples

Botstrap is quite flexible and (in theory) can easily adapt to work alongside any
[Discord library](https://discord.com/developers/docs/topics/community-resources#libraries)
written in Python. Nonetheless, real examples are always helpful! This directory
contains **"beginner bot"** templates for the libraries with which Botstrap has been
tested and confirmed to work.

If you'd like to run these examples yourself, the first thing you'll want to do is clone
this repo and navigate to this directory:

```
git clone https://github.com/nuztalgia/botstrap.git
cd botstrap/examples/libraries
```

<details>
<summary>
After that, run the commands in the sections for the libraries you'd like to try out.
(Using a <a href="https://docs.python.org/3/tutorial/venv.html">virtual environment</a>
is highly recommended.)
</summary><br>

&nbsp;&thinsp;&nbsp; **Each set of commands will:**

<div id="user-content-toc"><ol>
<li>Uninstall any/all existing Discord libraries (to prevent conflicts/confusion).</li>
<li>Install appropriate versions of the required packages for the selected example.</li>
<li>Run the Python module containing the example.</li>
</ol></div>

</details>

If there's another Python Discord library that you'd like to see included here, please
don't be shy to open a [pull request](/.github/CONTRIBUTING.md#pull-requests)! 💜

## <a href="./discordpy_bot"><img src="https://raw.githubusercontent.com/Rapptz/discord.py/master/docs/images/discord_py_logo.ico" width=24></a> discord.py

[![Botstrap Example](https://img.shields.io/badge/example-discordpy__bot-7e56c2.svg?logo=data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCI+PHBhdGggZmlsbD0iI2ZmZiIgZD0iTTIyIDE0SDIxQzIxIDEwLjEzIDE3Ljg3IDcgMTQgN0gxM1Y1LjczQzEzLjYgNS4zOSAxNCA0Ljc0IDE0IDRDMTQgMi45IDEzLjExIDIgMTIgMlMxMCAyLjkgMTAgNEMxMCA0Ljc0IDEwLjQgNS4zOSAxMSA1LjczVjdIMTBDNi4xMyA3IDMgMTAuMTMgMyAxNEgyQzEuNDUgMTQgMSAxNC40NSAxIDE1VjE4QzEgMTguNTUgMS40NSAxOSAyIDE5SDNWMjBDMyAyMS4xMSAzLjkgMjIgNSAyMkgxOUMyMC4xMSAyMiAyMSAyMS4xMSAyMSAyMFYxOUgyMkMyMi41NSAxOSAyMyAxOC41NSAyMyAxOFYxNUMyMyAxNC40NSAyMi41NSAxNCAyMiAxNE05Ljc5IDE2LjVDOS40IDE1LjYyIDguNTMgMTUgNy41IDE1UzUuNiAxNS42MiA1LjIxIDE2LjVDNS4wOCAxNi4xOSA1IDE1Ljg2IDUgMTUuNUM1IDE0LjEyIDYuMTIgMTMgNy41IDEzUzEwIDE0LjEyIDEwIDE1LjVDMTAgMTUuODYgOS45MiAxNi4xOSA5Ljc5IDE2LjVNMTguNzkgMTYuNUMxOC40IDE1LjYyIDE3LjUgMTUgMTYuNSAxNVMxNC42IDE1LjYyIDE0LjIxIDE2LjVDMTQuMDggMTYuMTkgMTQgMTUuODYgMTQgMTUuNUMxNCAxNC4xMiAxNS4xMiAxMyAxNi41IDEzUzE5IDE0LjEyIDE5IDE1LjVDMTkgMTUuODYgMTguOTIgMTYuMTkgMTguNzkgMTYuNVoiIC8+PC9zdmc+DQo=)](./discordpy_bot/__main__.py)
[![PyPI: Latest Version](https://img.shields.io/pypi/v/discord.py?logo=pypi&logoColor=fff&label=latest%20version)](https://pypi.org/project/discord.py/)
[![GitHub: Last Commit](https://img.shields.io/github/last-commit/Rapptz/discord.py?logo=github&logoColor=fff)](https://github.com/Rapptz/discord.py)

```
pip uninstall -r packages.txt -y
pip install -r discordpy_bot/requirements.txt
python -m discordpy_bot
```

## <a href="./disnake_bot"><img src="https://raw.githubusercontent.com/DisnakeDev/disnake/master/docs/images/disnake_logo.ico" width=24></a> disnake

[![Botstrap Example](https://img.shields.io/badge/example-disnake__bot-7e56c2.svg?logo=data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCI+PHBhdGggZmlsbD0iI2ZmZiIgZD0iTTIyIDE0SDIxQzIxIDEwLjEzIDE3Ljg3IDcgMTQgN0gxM1Y1LjczQzEzLjYgNS4zOSAxNCA0Ljc0IDE0IDRDMTQgMi45IDEzLjExIDIgMTIgMlMxMCAyLjkgMTAgNEMxMCA0Ljc0IDEwLjQgNS4zOSAxMSA1LjczVjdIMTBDNi4xMyA3IDMgMTAuMTMgMyAxNEgyQzEuNDUgMTQgMSAxNC40NSAxIDE1VjE4QzEgMTguNTUgMS40NSAxOSAyIDE5SDNWMjBDMyAyMS4xMSAzLjkgMjIgNSAyMkgxOUMyMC4xMSAyMiAyMSAyMS4xMSAyMSAyMFYxOUgyMkMyMi41NSAxOSAyMyAxOC41NSAyMyAxOFYxNUMyMyAxNC40NSAyMi41NSAxNCAyMiAxNE05Ljc5IDE2LjVDOS40IDE1LjYyIDguNTMgMTUgNy41IDE1UzUuNiAxNS42MiA1LjIxIDE2LjVDNS4wOCAxNi4xOSA1IDE1Ljg2IDUgMTUuNUM1IDE0LjEyIDYuMTIgMTMgNy41IDEzUzEwIDE0LjEyIDEwIDE1LjVDMTAgMTUuODYgOS45MiAxNi4xOSA5Ljc5IDE2LjVNMTguNzkgMTYuNUMxOC40IDE1LjYyIDE3LjUgMTUgMTYuNSAxNVMxNC42IDE1LjYyIDE0LjIxIDE2LjVDMTQuMDggMTYuMTkgMTQgMTUuODYgMTQgMTUuNUMxNCAxNC4xMiAxNS4xMiAxMyAxNi41IDEzUzE5IDE0LjEyIDE5IDE1LjVDMTkgMTUuODYgMTguOTIgMTYuMTkgMTguNzkgMTYuNVoiIC8+PC9zdmc+DQo=)](./disnake_bot/__main__.py)
[![PyPI: Latest Version](https://img.shields.io/pypi/v/disnake?logo=pypi&logoColor=fff&label=latest%20version)](https://pypi.org/project/disnake/)
[![GitHub: Last Commit](https://img.shields.io/github/last-commit/DisnakeDev/disnake?logo=github&logoColor=fff)](https://github.com/DisnakeDev/disnake)

```
pip uninstall -r packages.txt -y
pip install -r disnake_bot/requirements.txt
python -m disnake_bot
```

## <a href="./hikari_bot"><img src="https://raw.githubusercontent.com/hikari-py/hikari/master/pages/logo.png" width=24></a> hikari

[![Botstrap Example](https://img.shields.io/badge/example-hikari__bot-7e56c2.svg?logo=data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCI+PHBhdGggZmlsbD0iI2ZmZiIgZD0iTTIyIDE0SDIxQzIxIDEwLjEzIDE3Ljg3IDcgMTQgN0gxM1Y1LjczQzEzLjYgNS4zOSAxNCA0Ljc0IDE0IDRDMTQgMi45IDEzLjExIDIgMTIgMlMxMCAyLjkgMTAgNEMxMCA0Ljc0IDEwLjQgNS4zOSAxMSA1LjczVjdIMTBDNi4xMyA3IDMgMTAuMTMgMyAxNEgyQzEuNDUgMTQgMSAxNC40NSAxIDE1VjE4QzEgMTguNTUgMS40NSAxOSAyIDE5SDNWMjBDMyAyMS4xMSAzLjkgMjIgNSAyMkgxOUMyMC4xMSAyMiAyMSAyMS4xMSAyMSAyMFYxOUgyMkMyMi41NSAxOSAyMyAxOC41NSAyMyAxOFYxNUMyMyAxNC40NSAyMi41NSAxNCAyMiAxNE05Ljc5IDE2LjVDOS40IDE1LjYyIDguNTMgMTUgNy41IDE1UzUuNiAxNS42MiA1LjIxIDE2LjVDNS4wOCAxNi4xOSA1IDE1Ljg2IDUgMTUuNUM1IDE0LjEyIDYuMTIgMTMgNy41IDEzUzEwIDE0LjEyIDEwIDE1LjVDMTAgMTUuODYgOS45MiAxNi4xOSA5Ljc5IDE2LjVNMTguNzkgMTYuNUMxOC40IDE1LjYyIDE3LjUgMTUgMTYuNSAxNVMxNC42IDE1LjYyIDE0LjIxIDE2LjVDMTQuMDggMTYuMTkgMTQgMTUuODYgMTQgMTUuNUMxNCAxNC4xMiAxNS4xMiAxMyAxNi41IDEzUzE5IDE0LjEyIDE5IDE1LjVDMTkgMTUuODYgMTguOTIgMTYuMTkgMTguNzkgMTYuNVoiIC8+PC9zdmc+DQo=)](./hikari_bot/__main__.py)
[![PyPI: Latest Version](https://img.shields.io/pypi/v/hikari?logo=pypi&logoColor=fff&label=latest%20version&color=blue)](https://pypi.org/project/hikari/)
[![GitHub: Last Commit](https://img.shields.io/github/last-commit/hikari-py/hikari?logo=github&logoColor=fff)](https://github.com/hikari-py/hikari)

```
pip uninstall -r packages.txt -y
pip install -r hikari_bot/requirements.txt
python -m hikari_bot
```

## <a href="./interactions_bot"><img src="https://avatars.githubusercontent.com/u/98242689" width=24></a> interactions.py

[![Botstrap Example](https://img.shields.io/badge/example-interactions__bot-7e56c2.svg?logo=data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCI+PHBhdGggZmlsbD0iI2ZmZiIgZD0iTTIyIDE0SDIxQzIxIDEwLjEzIDE3Ljg3IDcgMTQgN0gxM1Y1LjczQzEzLjYgNS4zOSAxNCA0Ljc0IDE0IDRDMTQgMi45IDEzLjExIDIgMTIgMlMxMCAyLjkgMTAgNEMxMCA0Ljc0IDEwLjQgNS4zOSAxMSA1LjczVjdIMTBDNi4xMyA3IDMgMTAuMTMgMyAxNEgyQzEuNDUgMTQgMSAxNC40NSAxIDE1VjE4QzEgMTguNTUgMS40NSAxOSAyIDE5SDNWMjBDMyAyMS4xMSAzLjkgMjIgNSAyMkgxOUMyMC4xMSAyMiAyMSAyMS4xMSAyMSAyMFYxOUgyMkMyMi41NSAxOSAyMyAxOC41NSAyMyAxOFYxNUMyMyAxNC40NSAyMi41NSAxNCAyMiAxNE05Ljc5IDE2LjVDOS40IDE1LjYyIDguNTMgMTUgNy41IDE1UzUuNiAxNS42MiA1LjIxIDE2LjVDNS4wOCAxNi4xOSA1IDE1Ljg2IDUgMTUuNUM1IDE0LjEyIDYuMTIgMTMgNy41IDEzUzEwIDE0LjEyIDEwIDE1LjVDMTAgMTUuODYgOS45MiAxNi4xOSA5Ljc5IDE2LjVNMTguNzkgMTYuNUMxOC40IDE1LjYyIDE3LjUgMTUgMTYuNSAxNVMxNC42IDE1LjYyIDE0LjIxIDE2LjVDMTQuMDggMTYuMTkgMTQgMTUuODYgMTQgMTUuNUMxNCAxNC4xMiAxNS4xMiAxMyAxNi41IDEzUzE5IDE0LjEyIDE5IDE1LjVDMTkgMTUuODYgMTguOTIgMTYuMTkgMTguNzkgMTYuNVoiIC8+PC9zdmc+DQo=)](./interactions_bot/__main__.py)
[![PyPI: Latest Version](https://img.shields.io/pypi/v/discord-py-interactions?logo=pypi&logoColor=fff&label=latest%20version)](https://pypi.org/project/discord-py-interactions/)
[![GitHub: Last Commit](https://img.shields.io/github/last-commit/interactions-py/library?logo=github&logoColor=fff)](https://github.com/interactions-py/library)

```
pip uninstall -r packages.txt -y
pip install -r interactions_bot/requirements.txt
python -m interactions_bot
```

## <a href="./naff_bot"><img src="https://avatars.githubusercontent.com/u/91958504" width=24></a> NAFF

[![Botstrap Example](https://img.shields.io/badge/example-naff__bot-7e56c2.svg?logo=data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCI+PHBhdGggZmlsbD0iI2ZmZiIgZD0iTTIyIDE0SDIxQzIxIDEwLjEzIDE3Ljg3IDcgMTQgN0gxM1Y1LjczQzEzLjYgNS4zOSAxNCA0Ljc0IDE0IDRDMTQgMi45IDEzLjExIDIgMTIgMlMxMCAyLjkgMTAgNEMxMCA0Ljc0IDEwLjQgNS4zOSAxMSA1LjczVjdIMTBDNi4xMyA3IDMgMTAuMTMgMyAxNEgyQzEuNDUgMTQgMSAxNC40NSAxIDE1VjE4QzEgMTguNTUgMS40NSAxOSAyIDE5SDNWMjBDMyAyMS4xMSAzLjkgMjIgNSAyMkgxOUMyMC4xMSAyMiAyMSAyMS4xMSAyMSAyMFYxOUgyMkMyMi41NSAxOSAyMyAxOC41NSAyMyAxOFYxNUMyMyAxNC40NSAyMi41NSAxNCAyMiAxNE05Ljc5IDE2LjVDOS40IDE1LjYyIDguNTMgMTUgNy41IDE1UzUuNiAxNS42MiA1LjIxIDE2LjVDNS4wOCAxNi4xOSA1IDE1Ljg2IDUgMTUuNUM1IDE0LjEyIDYuMTIgMTMgNy41IDEzUzEwIDE0LjEyIDEwIDE1LjVDMTAgMTUuODYgOS45MiAxNi4xOSA5Ljc5IDE2LjVNMTguNzkgMTYuNUMxOC40IDE1LjYyIDE3LjUgMTUgMTYuNSAxNVMxNC42IDE1LjYyIDE0LjIxIDE2LjVDMTQuMDggMTYuMTkgMTQgMTUuODYgMTQgMTUuNUMxNCAxNC4xMiAxNS4xMiAxMyAxNi41IDEzUzE5IDE0LjEyIDE5IDE1LjVDMTkgMTUuODYgMTguOTIgMTYuMTkgMTguNzkgMTYuNVoiIC8+PC9zdmc+DQo=)](./naff_bot/__main__.py)
[![PyPI: Latest Version](https://img.shields.io/pypi/v/naff?logo=pypi&logoColor=fff&label=latest%20version)](https://pypi.org/project/naff/)
[![GitHub: Last Commit](https://img.shields.io/github/last-commit/NAFTeam/NAFF?logo=github&logoColor=fff)](https://github.com/NAFTeam/NAFF)

```
pip uninstall -r packages.txt -y
pip install -r naff_bot/requirements.txt
python -m naff_bot
```

## <a href="./nextcord_bot"><img src="https://raw.githubusercontent.com/nextcord/nextcord/master/docs/images/nextcord_logo.ico" width=24></a> Nextcord

[![Botstrap Example](https://img.shields.io/badge/example-nextcord__bot-7e56c2.svg?logo=data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCI+PHBhdGggZmlsbD0iI2ZmZiIgZD0iTTIyIDE0SDIxQzIxIDEwLjEzIDE3Ljg3IDcgMTQgN0gxM1Y1LjczQzEzLjYgNS4zOSAxNCA0Ljc0IDE0IDRDMTQgMi45IDEzLjExIDIgMTIgMlMxMCAyLjkgMTAgNEMxMCA0Ljc0IDEwLjQgNS4zOSAxMSA1LjczVjdIMTBDNi4xMyA3IDMgMTAuMTMgMyAxNEgyQzEuNDUgMTQgMSAxNC40NSAxIDE1VjE4QzEgMTguNTUgMS40NSAxOSAyIDE5SDNWMjBDMyAyMS4xMSAzLjkgMjIgNSAyMkgxOUMyMC4xMSAyMiAyMSAyMS4xMSAyMSAyMFYxOUgyMkMyMi41NSAxOSAyMyAxOC41NSAyMyAxOFYxNUMyMyAxNC40NSAyMi41NSAxNCAyMiAxNE05Ljc5IDE2LjVDOS40IDE1LjYyIDguNTMgMTUgNy41IDE1UzUuNiAxNS42MiA1LjIxIDE2LjVDNS4wOCAxNi4xOSA1IDE1Ljg2IDUgMTUuNUM1IDE0LjEyIDYuMTIgMTMgNy41IDEzUzEwIDE0LjEyIDEwIDE1LjVDMTAgMTUuODYgOS45MiAxNi4xOSA5Ljc5IDE2LjVNMTguNzkgMTYuNUMxOC40IDE1LjYyIDE3LjUgMTUgMTYuNSAxNVMxNC42IDE1LjYyIDE0LjIxIDE2LjVDMTQuMDggMTYuMTkgMTQgMTUuODYgMTQgMTUuNUMxNCAxNC4xMiAxNS4xMiAxMyAxNi41IDEzUzE5IDE0LjEyIDE5IDE1LjVDMTkgMTUuODYgMTguOTIgMTYuMTkgMTguNzkgMTYuNVoiIC8+PC9zdmc+DQo=)](./nextcord_bot/__main__.py)
[![PyPI: Latest Version](https://img.shields.io/pypi/v/nextcord?logo=pypi&logoColor=fff&label=latest%20version)](https://pypi.org/project/nextcord/)
[![GitHub: Last Commit](https://img.shields.io/github/last-commit/nextcord/nextcord?logo=github&logoColor=fff)](https://github.com/nextcord/nextcord)

```
pip uninstall -r packages.txt -y
pip install -r nextcord_bot/requirements.txt
python -m nextcord_bot
```

## <a href="./pycord_bot"><img src="https://github.com/Pycord-Development/pycord/blob/master/docs/images/pycord_logo.png" width=24></a> Pycord

[![Botstrap Example](https://img.shields.io/badge/example-pycord__bot-7e56c2.svg?logo=data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCI+PHBhdGggZmlsbD0iI2ZmZiIgZD0iTTIyIDE0SDIxQzIxIDEwLjEzIDE3Ljg3IDcgMTQgN0gxM1Y1LjczQzEzLjYgNS4zOSAxNCA0Ljc0IDE0IDRDMTQgMi45IDEzLjExIDIgMTIgMlMxMCAyLjkgMTAgNEMxMCA0Ljc0IDEwLjQgNS4zOSAxMSA1LjczVjdIMTBDNi4xMyA3IDMgMTAuMTMgMyAxNEgyQzEuNDUgMTQgMSAxNC40NSAxIDE1VjE4QzEgMTguNTUgMS40NSAxOSAyIDE5SDNWMjBDMyAyMS4xMSAzLjkgMjIgNSAyMkgxOUMyMC4xMSAyMiAyMSAyMS4xMSAyMSAyMFYxOUgyMkMyMi41NSAxOSAyMyAxOC41NSAyMyAxOFYxNUMyMyAxNC40NSAyMi41NSAxNCAyMiAxNE05Ljc5IDE2LjVDOS40IDE1LjYyIDguNTMgMTUgNy41IDE1UzUuNiAxNS42MiA1LjIxIDE2LjVDNS4wOCAxNi4xOSA1IDE1Ljg2IDUgMTUuNUM1IDE0LjEyIDYuMTIgMTMgNy41IDEzUzEwIDE0LjEyIDEwIDE1LjVDMTAgMTUuODYgOS45MiAxNi4xOSA5Ljc5IDE2LjVNMTguNzkgMTYuNUMxOC40IDE1LjYyIDE3LjUgMTUgMTYuNSAxNVMxNC42IDE1LjYyIDE0LjIxIDE2LjVDMTQuMDggMTYuMTkgMTQgMTUuODYgMTQgMTUuNUMxNCAxNC4xMiAxNS4xMiAxMyAxNi41IDEzUzE5IDE0LjEyIDE5IDE1LjVDMTkgMTUuODYgMTguOTIgMTYuMTkgMTguNzkgMTYuNVoiIC8+PC9zdmc+DQo=)](./pycord_bot/__main__.py)
[![PyPI: Latest Version](https://img.shields.io/pypi/v/py-cord?logo=pypi&logoColor=fff&label=latest%20version)](https://pypi.org/project/py-cord/)
[![GitHub: Last Commit](https://img.shields.io/github/last-commit/Pycord-Development/pycord?logo=github&logoColor=fff)](https://github.com/Pycord-Development/pycord)

```
pip uninstall -r packages.txt -y
pip install -r pycord_bot/requirements.txt
python -m pycord_bot
```
