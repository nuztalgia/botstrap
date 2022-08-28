## Botstrap {#}

<!-- prettier-ignore -->
::: botstrap.Botstrap
    options:
      heading_level: 1
      members: false

??? abstract "Diagram - The Botstrap Flowchart"

    <div id="botstrap-flowchart"/>
    <figure markdown>
      ```mermaid
      flowchart TB
          A{{"&thinsp;__init__()&thinsp;&emsp;&emsp;"}}
          A --> B("Do you want to use a custom bot token?")
          B -- Yes --> C{{"&thinsp;register_token()&thinsp;&emsp;&emsp;"}}
          C --> D("Do you have more tokens?")
          D -- Yes --> C
          D -- No --> E("Do you want to customize the CLI?")
          B -- No --> E
          E -- Yes --> F{{"&thinsp;parse_args()&ensp;&emsp;"}}
          F --> G("Is your bot simple to instantiate?")
          E -- No --> G
          G -- Yes --> H{{"&thinsp;run_bot()&ensp;&emsp;"}}
          G -- No --> I{{"&thinsp;retrieve_active_token() &ensp;&emsp;&emsp;"}}
          I --> J("Plug the result into your bot.")
          H --> K(("Done!"))
          J --> K

          click A "#botstrap.flow.Botstrap.__init__"
          click C "#botstrap.flow.Botstrap.register_token"
          click F "#botstrap.flow.Botstrap.parse_args"
          click H "#botstrap.flow.Botstrap.run_bot"
          click I "#botstrap.flow.Botstrap.retrieve_active_token"

          class A,C,F,H,I method;
          classDef method font-family: Roboto Mono, font-size: 14px, font-weight: bold
          classDef method fill: #7c4dff66, stroke: #7c4dffff, stroke-width: 2px

          class B,D,E,G,J textBox;
          classDef textBox fill: #00b0ff11, stroke: #00b0ff33, stroke-width: 2px

          class K lastNode;
          classDef lastNode fill: #00c85366, stroke: #00c853cc
          classDef lastNode font-weight: bold, stroke-width: 2px

          linkStyle 1,3,6,9 opacity: 0.9, stroke-dasharray: 8 4
          linkStyle 4,5,8,10 opacity: 0.9, stroke-dasharray: 5 6
          linkStyle 0,2,7,11,12,13 opacity: 0.9, stroke-width: 3px
      ```
    </figure>

??? example "Example - Putting it all together"

    <div id="full-example"/>
    === "Intro"
        ```{.text .line-numbers-off}
        📁 workspace/
        └── 📁 examplebot/
            ├── 📄 __main__.py
            └── 📄 extras.py
        ```

        This is an extensive, multi-part example that utilizes the directory structure
        outlined above.

        If any of the code or console output in the following tabs is unclear, try using
        the search bar at the top of the page to look up the key terms and read through
        the relevant documentation, then come back to this example.

        (And if the docs aren't helpful, please do start a
        [discussion](https://github.com/nuztalgia/botstrap/discussions)
        about what could be clarified!)

        ---
        The next two tabs (after this "Intro" tab) provide the contents of the **Python
        files** used in this example:

        - `__main__.py` - This file contains the entire Botstrap integration and
        exercises all of the recommended methods in this class, as well as a few other
        classes that are also part of Botstrap's [public API](..).
        - `extras.py` - This file represents a very small subset of the extra pieces
        that a Discord bot might have. Its purpose is simply to provide more context
        for the integration, so feel free to skip it if you don't find it useful.

        ---
        The subsequent tabs demonstrate the **CLI output** for various program flows
        and/or command-line arguments:

        1. `python -m examplebot -h` - The help menu for the example bot.
        2. `python -m examplebot` - Running the bot in its default (`dev`) mode for the
           first time; going through the flow for adding a token **without** a password.

    === "\_\_main\_\_.py"
        ```py
        {% include "../../examples/ex1/__main__.py" %}
        ```

    === "extras.py"
        ```py
        {% include "../../examples/ex1/extras.py" %}
        ```

    === "CLI #1"
        ```console
        $ python -m examplebot -h
        usage: examplebot [-l <str>] [-a] [--allow-pings] [-t] [--help] [<token id>]

          A really cool Discord bot that uses Botstrap!
          Run "python -m examplebot" with no parameters to start the bot in development mode.

        positional arguments:
        {% include "../../examples/README.md" start="positional arguments:\n" end="```" %}
        ```

    === "CLI #2"
        ```console
        $ python -m examplebot

        example-bot: You currently don't have a saved development bot token.
        Would you like to add one now? If so, type "yes" or "y": y

        Please enter your bot token now. It'll be invisible for security reasons.
        BOT TOKEN: ************************.******.***************************

        Your token has been successfully encrypted and saved.

        Do you want to use this token to run your bot now? If so, type "yes" or "y": y

        example-bot: development: Attempting to log in to Discord...
        example-bot: development: Successfully logged in as "BasicBot#1234".
        ```

<!-- prettier-ignore -->
::: botstrap.Botstrap
    options:
      show_root_heading: false
      show_root_toc_entry: false
      show_signature_annotations: false

<link rel="stylesheet" href="../stylesheets/botstrap.css" />
<link rel="stylesheet" href="../../stylesheets/code-navigation.css" />
<link rel="stylesheet" href="../../stylesheets/hide-dupe-class.css" />
<link rel="stylesheet" href="../../stylesheets/material-tabs.css" />
