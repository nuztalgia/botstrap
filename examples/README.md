# <a href="https://botstrap.rtfd.io"><img src="/docs/images/logo-48.png" width=24></a> Examples

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
<summary>If everything was set up correctly, you should see a help menu that looks something like this... <i>(click to expand)</i></summary>

```text
usage: examplebot [-l <int>] [-s <str>] [-a <str>] [-m] [-t] [--help] [<token id>]

  A really cool Discord bot that uses Botstrap!
  Run "python -m examplebot" with no parameters to start the bot in development mode.

positional arguments:
  <token id>            The ID of the token to use to run the bot.
                        Valid options are "dev" and "prod".

options:
  -l <>, --log-thld <>  A value from 1-4 specifying the minimum log threshold.
  -s <>, --status <>    Text to show in the bot's Discord profile status.
  -a <>, --activity <>  The text preceding '--status'. Defaults to 'playing'.
  -m, --mentions        Allow the bot to @mention members and/or roles.
  -t, --tokens          View/manage your saved Discord bot tokens.
  -h, --help            Display this help message.
```

</details>

Once that's working, go ahead and play around with the available command-line options,
and observe the resulting behavior! :tada:
