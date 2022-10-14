# <a href="https://botstrap.rtfd.io"><img src="/docs/images/logo-48.png" width=24></a> Examples

While (in theory) Botstrap should be able to work alongside any Discord API wrapper
written in Python, the following libraries have been explicitly tested and are therefore
officially supported by Botstrap and the examples on this page:

|    Library Name     | GitHub                                                                                                                         | PyPI                                                                                                                | Install                                  |
| :-----------------: | ------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------- | ---------------------------------------- |
|   **discord.py**    | [![GitHub](https://img.shields.io/github/last-commit/Rapptz/discord.py)](https://github.com/Rapptz/discord.py)                 | [![PyPI](https://img.shields.io/pypi/v/discord.py)](https://pypi.org/project/discord.py/)                           | `pip install -U discord.py`              |
|     **disnake**     | [![GitHub](https://img.shields.io/github/last-commit/DisnakeDev/disnake)](https://github.com/DisnakeDev/disnake)               | [![PyPI](https://img.shields.io/pypi/v/disnake)](https://pypi.org/project/disnake/)                                 | `pip install -U disnake`                 |
|     **hikari**      | [![GitHub](https://img.shields.io/github/last-commit/hikari-py/hikari)](https://github.com/hikari-py/hikari)                   | [![PyPI](https://img.shields.io/pypi/v/hikari)](https://pypi.org/project/hikari/)                                   | `pip install -U hikari`                  |
| **interactions.py** | [![GitHub](https://img.shields.io/github/last-commit/interactions-py/library)](https://github.com/interactions-py/library)     | [![PyPI](https://img.shields.io/pypi/v/discord-py-interactions)](https://pypi.org/project/discord-py-interactions/) | `pip install -U discord-py-interactions` |
|      **NAFF**       | [![GitHub](https://img.shields.io/github/last-commit/NAFTeam/NAFF)](https://github.com/NAFTeam/NAFF)                           | [![PyPI](https://img.shields.io/pypi/v/naff)](https://pypi.org/project/naff/)                                       | `pip install -U naff`                    |
|    **Nextcord**     | [![GitHub](https://img.shields.io/github/last-commit/nextcord/nextcord)](https://github.com/nextcord/nextcord)                 | [![PyPI](https://img.shields.io/pypi/v/nextcord)](https://pypi.org/project/nextcord/)                               | `pip install -U nextcord`                |
|     **Pycord**      | [![GitHub](https://img.shields.io/github/last-commit/Pycord-Development/pycord)](https://github.com/Pycord-Development/pycord) | [![PyPI](https://img.shields.io/pypi/v/py-cord)](https://pypi.org/project/py-cord/)                                 | `pip install -U py-cord`                 |

If there's another Python Discord library that you'd like to see supported and/or
included in this list, feel free to open a
[pull request](../.github/CONTRIBUTING.md#pull-requests)! 💜

## Simple Demo

No files needed! Assuming you have one of the supported Discord libraries installed,
just run the following command in your terminal:

```sh
python -c "from botstrap import *; Botstrap().run_bot()"
```

This is the absolute simplest use case. It assumes that the bot doesn't have any special
behavior or CLI options, and only uses one bot token.

Although this example is unlikely to be applicable in practice, it's a nice minimal
demonstration of Botstrap's default settings and flow.

## Actual Example

This example is much more informative. It uses the
[Pycord](https://pypi.org/project/py-cord/) library and the following files from the
[`examplebot`](examplebot/) directory:

<ul>
<li><details open><summary>
<a href="examplebot/__main__.py"><code>__main__.py</code></a> - Contains the entire
Botstrap integration and exercises all the recommended methods in the
<a href="https://botstrap.rtfd.io/en/latest/api/botstrap/#botstrap-flowchart"><code>Botstrap</code></a>
flow, as well as a few other classes that are also part of the public
<a href="https://botstrap.rtfd.io/en/latest/api/">API</a>. This file is a good reference
for what a fully-fledged integration might look like.</summary>

https://github.com/nuztalgia/botstrap/blob/453499457b48f579b6eec779832c1ac00464220e/examples/examplebot/__main__.py#L1-L46

</details></li>
<li><details><summary>
<a href="examplebot/extras.py"><code>extras.py</code></a> - Represents a very small
subset of the non-Botstrap-related components that a Discord bot might have. The purpose
of this file is simply to provide more context for the example integration, so feel free
to skip over it if you don't find it useful.</summary>

https://github.com/nuztalgia/botstrap/blob/453499457b48f579b6eec779832c1ac00464220e/examples/examplebot/extras.py#L1-L41

</details>
</ul>

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
