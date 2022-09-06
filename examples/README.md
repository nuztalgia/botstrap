# <a href="https://botstrap.rtfd.io"><img src="/docs/images/logo-48.png" width=24></a> Examples

Except where specified [otherwise](#example-2), these examples assume that you have
either [discord.py](https://github.com/Rapptz/discord.py) **or**
[Pycord](https://github.com/Pycord-Development/pycord) installed. This is because both
of these libraries export `discord.Bot`, which is the default class targeted by
[`run_bot()`](https://botstrap.rtfd.io/en/latest/api/botstrap/#botstrap.flow.Botstrap.run_bot).
In theory, other libraries that use the `discord` namespace could also work, but have
not been tested.

## Example #0

No files needed! Just run the following command in your terminal:

```sh
python -c "from botstrap import *; Botstrap().run_bot()"
```

This is the absolute simplest use case. It assumes that the bot:

- Only uses a single bot token, named `default`.
- Does not need/want to customize its CLI at all.
- Is of the type `discord.Bot` (i.e. not a
  [subclass](https://guide.pycord.dev/popular-topics/subclassing-bots/)).

Although this example is unlikely to be applicable in practice, it's a nice minimal
demonstration of Botstrap's default settings and flow.

## Example #1

This example is significantly more involved, and uses the following two files:

- [`examplebot/__main__.py`](examplebot/__main__.py) - Contains the entire Botstrap
  integration and exercises all the recommended methods in the
  [`Botstrap`](https://botstrap.rtfd.io/en/latest/api/botstrap/#botstrap-flowchart)
  flow, as well as a few other classes that are also part of the public
  [API](https://botstrap.rtfd.io/en/latest/api/).

- [`examplebot/extras.py`](examplebot/extras.py) - Represents a very small subset of the
  extra pieces that a Discord bot might have. The purpose of this file is simply to
  provide more context for the example integration, so feel free to skip over it if you
  don't find it useful.

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

## Example #2

This example is less about Botstrap's features, and more about the Discord libraries
that it supports. While (in theory) Botstrap can work with any Discord API wrapper
written in Python, the following libraries have been explicitly tested and are therefore
included in this example:

<table><tr align="center">
<th width=200><a href="https://github.com/Rapptz/discord.py">discord.py</a></td>
<th width=200><a href="https://github.com/DisnakeDev/disnake">disnake</a></td>
<th width=200><a href="https://github.com/hikari-py/hikari">hikari</a></td>
<th width=200><a href="https://github.com/interactions-py/library">interactions.py</a></td>
<th width=200><a href="https://github.com/NAFTeam/NAFF">NAFF</a></td>
<th width=200><a href="https://github.com/nextcord/nextcord">Nextcord</a></td>
<th width=200><a href="https://github.com/Pycord-Development/pycord">Pycord</a></td>
</tr></table>

The relevant files for this example are:

- [`librarybot/__main__.py`](librarybot/__main__.py) - Again, this file holds the entire
  Botstrap integration, but is very different from the one in the previous example. Its
  most important feature is the `-l` command-line option, which allows you to select a
  specific Discord library for the bot to use.

- [`librarybot/libraries.py`](librarybot/libraries.py) - Contains utility functions that
  make use of the [`importlib`](https://docs.python.org/3/library/importlib.html) module
  as well as Botstrap's internal
  [`Metadata`](https://botstrap.rtfd.io/en/latest/internal/metadata/) class to determine
  which of the supported Discord libraries are installed, and to import the bot class
  from the one that is selected.

As usual, the bot must be run from **this directory** (i.e. `examples` - not
`librarybot`). This command will run the bot using the first library it finds:

```sh
python -m librarybot
```

If you have **more than one** of the supported libraries installed, the `--library` (or
`-l` for short) command-line option will be available, and you may specify the one to
use by providing its namespace. Note that the `discord` namespace is ambiguous, as both
**discord.py** and **Pycord** use it.

Here's what a failed (for educational purposes) command looks like when you have all of
the libraries **except** the `discord` ones installed:

```sh
python -m librarybot -l ?
usage: librarybot [-l <str>] [-t] [--help]
librarybot: error: argument -l/--library: invalid choice: '?' (choose from 'disnake', 'hikari', 'interactions', 'naff', 'nextcord')
```

If there's another Python Discord library that you'd like to see included in this
example, feel free to open a [pull request](../.github/CONTRIBUTING.md#pull-requests)!
💜
