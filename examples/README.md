# <a href="https://botstrap.rtfd.io"><img src="/docs/images/logo-48.png" width=24></a> Examples

While (in theory) Botstrap should be able to work alongside any Discord API wrapper
written in Python, the following libraries have been explicitly tested and are therefore
officially supported by Botstrap and the examples on this page:

<table><tr align="center">
<th width=200><a href="https://github.com/Rapptz/discord.py">discord.py</a></td>
<th width=200><a href="https://github.com/DisnakeDev/disnake">disnake</a></td>
<th width=200><a href="https://github.com/hikari-py/hikari">hikari</a></td>
<th width=200><a href="https://github.com/interactions-py/library">interactions.py</a></td>
<th width=200><a href="https://github.com/NAFTeam/NAFF">NAFF</a></td>
<th width=200><a href="https://github.com/nextcord/nextcord">Nextcord</a></td>
<th width=200><a href="https://github.com/Pycord-Development/pycord">Pycord</a></td>
</tr></table>

If there's another Python Discord library that you'd like to see supported and/or
included in this list, feel free to open a
[pull request](../.github/CONTRIBUTING.md#pull-requests)! 💜

## Example #0

No files needed! Assuming you have one of the supported Discord libraries installed,
just run the following command in your terminal:

```sh
python -c "from botstrap import *; Botstrap().run_bot()"
```

This is the absolute simplest use case. It assumes that the bot doesn't have any special
behavior or CLI options, and only uses one bot token.

Although this example is unlikely to be applicable in practice, it's a nice minimal
demonstration of Botstrap's default settings and flow.

## Example #1

This example lets you try out a slightly-less-minimal Botstrap integration using the
Discord library of your choice, and serves as a reference for how to get started using
Botstrap with each of the supported Discord libraries. All of the code for this example
is contained in [`librarybot.py`](librarybot.py).

LibraryBot features the `--library` (or `-l` for short) command-line option, which
allows you to select a specific Discord library for the bot to use. This option should
be followed by the library's unique ID. Let's try it out with Pycord, since that's the
library required by the next example:

```sh
python librarybot.py -l pycord
```

Of course, you can use the name of any other supported library, and you're encouraged to
try more than one to see what works best for you.

<details>
<summary>Here's a table containing the IDs, GitHub/PyPI links, and installation commands
for all of the offically-supported libraries... <i>(click to expand)</i></summary><br>

|    Library Name     | LibraryBot ID  | GitHub                                                                                                                         | PyPI                                                                                                                | Install                                  |
| :-----------------: | :------------: | ------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------- | ---------------------------------------- |
|   **discord.py**    |  `discordpy`   | [![GitHub](https://img.shields.io/github/last-commit/Rapptz/discord.py)](https://github.com/Rapptz/discord.py)                 | [![PyPI](https://img.shields.io/pypi/v/discord.py)](https://pypi.org/project/discord.py/)                           | `pip install -U discord.py`              |
|     **disnake**     |   `disnake`    | [![GitHub](https://img.shields.io/github/last-commit/DisnakeDev/disnake)](https://github.com/DisnakeDev/disnake)               | [![PyPI](https://img.shields.io/pypi/v/disnake)](https://pypi.org/project/disnake/)                                 | `pip install -U disnake`                 |
|     **hikari**      |    `hikari`    | [![GitHub](https://img.shields.io/github/last-commit/hikari-py/hikari)](https://github.com/hikari-py/hikari)                   | [![PyPI](https://img.shields.io/pypi/v/hikari)](https://pypi.org/project/hikari/)                                   | `pip install -U hikari`                  |
| **interactions.py** | `interactions` | [![GitHub](https://img.shields.io/github/last-commit/interactions-py/library)](https://github.com/interactions-py/library)     | [![PyPI](https://img.shields.io/pypi/v/discord-py-interactions)](https://pypi.org/project/discord-py-interactions/) | `pip install -U discord-py-interactions` |
|      **NAFF**       |     `naff`     | [![GitHub](https://img.shields.io/github/last-commit/NAFTeam/NAFF)](https://github.com/NAFTeam/NAFF)                           | [![PyPI](https://img.shields.io/pypi/v/naff)](https://pypi.org/project/naff/)                                       | `pip install -U naff`                    |
|    **Nextcord**     |   `nextcord`   | [![GitHub](https://img.shields.io/github/last-commit/nextcord/nextcord)](https://github.com/nextcord/nextcord)                 | [![PyPI](https://img.shields.io/pypi/v/nextcord)](https://pypi.org/project/nextcord/)                               | `pip install -U nextcord`                |
|     **Pycord**      |    `pycord`    | [![GitHub](https://img.shields.io/github/last-commit/Pycord-Development/pycord)](https://github.com/Pycord-Development/pycord) | [![PyPI](https://img.shields.io/pypi/v/py-cord)](https://pypi.org/project/py-cord/)                                 | `pip install -U py-cord`                 |

</details>

## Example #2

This example is much more realistic than the previous ones. It uses the
[Pycord](https://pypi.org/project/py-cord/) library and the following files from the
[`examplebot`](examplebot/) directory:

- [`__main__.py`](examplebot/__main__.py) - Contains the entire Botstrap integration and
  exercises all the recommended methods in the
  [`Botstrap`](https://botstrap.rtfd.io/en/latest/api/botstrap/#botstrap-flowchart)
  flow, as well as a few other classes that are also part of the public
  [API](https://botstrap.rtfd.io/en/latest/api/). This file is a good reference for what
  a sophisticated integration might look like.

- [`extras.py`](examplebot/extras.py) - Represents a very small subset of the
  non-Botstrap-related components that a Discord bot might have. The purpose of this
  file is simply to provide more context for the example integration, so feel free to
  skip over it if you don't find it useful.

While the files for this example are contained within their own subdirectory, the
command to run their code must be executed in **this directory** (i.e. `examples` - not
`examplebot`). After making sure you're in the correct working directory, run the
following command in your terminal:

```sh
python -m examplebot -h
```

<details>
<summary>If everything was set up correctly, you should see a help menu that looks
something like this... <i>(click to expand)</i></summary>

```text
usage: examplebot [-l <int>] [-s <str>] [-a <str>] [-m] [-t] [--help] [<token id>]

  A really cool Discord bot that uses Botstrap!
  Run "python -m examplebot" with no parameters to start the bot in development mode.

positional arguments:
  <token id>            The ID of the token to use to run the bot.
                        Valid options are "dev" and "prod".

options:
  -l <>, --loglevel <>  A value from 1 to 4 specifying the minimum log level.
  -s <>, --status <>    Text to show in the bot's Discord profile status.
  -a <>, --activity <>  The text preceding '--status'. Defaults to 'playing'.
  -m, --mentions        Allow the bot to @mention members and/or roles.
  -t, --tokens          View/manage your saved Discord bot tokens.
  -h, --help            Display this help message.
```

</details>

Once that's working, go ahead and play around with the available command-line options,
and observe the resulting behavior! :tada:
