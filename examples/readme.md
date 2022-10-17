# <a href="https://botstrap.rtfd.io"><img src="/docs/images/logo-48.png" width=24></a> Examples

## Simple CLI Demo

No files needed! Assuming you have [Botstrap](/../../#installation) and one of the
[supported Discord libraries](./libraries) installed, just run this command in your
terminal:

```sh
python -c "from botstrap import *; Botstrap().run_bot()"
```

This is the absolute simplest use case. It assumes that the bot doesn't have any special
behavior or CLI options, and only uses one bot token.

Although this example may not be applicable in practice, it's a nice minimal
demonstration of Botstrap's default settings & token creation flow.

## Retrieving a Token

If you have an existing Discord bot project, you probably have some code that looks like
one of the following lines:

```py
token = os.getenv("TOKEN")  # Using dotenv, because environment variables are "safe".
token = config.TOKEN  # Importing a plaintext value from a git-ignored config file.
token = "<token value>"  # Self-explanatory. Please, at the very least, don't do this.
```

You can replace that code with this Botstrap
[one-liner](https://botstrap.readthedocs.io/en/latest/api/botstrap/#botstrap.flow.Botstrap.retrieve_active_token),
which will encrypt your bot token so that it's never stored on your system in plaintext:

```py
token = Botstrap().retrieve_active_token()
```

Of course, there are a lot more options available - you can customize how each token
appears in the CLI, whether it requires a password to decrypt, and where its encrypted
files are stored. If your bot uses multiple tokens, simply
[register](https://botstrap.readthedocs.io/en/latest/api/botstrap/#botstrap.flow.Botstrap.register_token)
all of them and use a command-line option (automatically created for you) to select
which to use when you run the bot (e.g. `python bot.py` vs. `python bot.py prod` for
this next snippet).

```py
token = (
    Botstrap()
    .register_token(uid="dev", display_name=Color.yellow("development"))
    .register_token(uid="prod", requires_password=True, display_name=Color.green("production"))
    .retrieve_active_token()
)
```

## Comprehensive Example

This example uses the [Pycord](https://pypi.org/project/py-cord/) library along with the
following two files from the [`examplebot`](./examplebot) directory:

<ul>
<li><details open><summary>
<a href="./examplebot/__main__.py"><code>__main__.py</code></a> - Contains the entire
Botstrap integration and exercises all the recommended methods in the
<a href="https://botstrap.rtfd.io/en/latest/api/botstrap/#botstrap-flowchart"><code>Botstrap</code></a>
flow, as well as a few other classes that are also part of the public
<a href="https://botstrap.rtfd.io/en/latest/api/">API</a>. This file is a good reference
for what a fully-fledged integration might look like.</summary>

https://github.com/nuztalgia/botstrap/blob/3b94b3b93f8d13ecd530e0f7e3e258b580c8141c/examples/examplebot/__main__.py#L1-L46

</details></li>
<li><details><summary>
<a href="./examplebot/extras.py"><code>extras.py</code></a> - Represents a very small
subset of the non-Botstrap-related components that a Discord bot might have. The purpose
of this file is simply to provide more context for the example integration, so feel free
to skip over it if you don't find it useful.</summary>

https://github.com/nuztalgia/botstrap/blob/3b94b3b93f8d13ecd530e0f7e3e258b580c8141c/examples/examplebot/extras.py#L1-L41

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
