<!-- prettier-ignore -->
::: botstrap.Botstrap
    options:
      heading_level: 1
      members: false

For an overview of this class's usage, see the flowchart below. It establishes a
foundation for the subsequent example, which includes code snippets and demonstrates the
**CLI** (command-line interface) created by a lightly-customized Botstrap integration.

??? abstract "Diagram - The Botstrap Flowchart"

    <div id="botstrap-flowchart"/>
    The following diagram provides a high-level roadmap for this class and illustrates
    which methods are (and aren't) necessary to invoke as you proceed through the flow.
    Start at the top, and click on each method name that you encounter on the way down
    for more detailed information and usage instructions.

    <figure markdown>
      ```mermaid
      flowchart TB
          A{{"&thinsp;__init__()&thinsp;&emsp;&emsp;"}}
          A --> B("Do you want to use a custom bot token?")
          B -- Yes --> C{{"&thinsp;register_token()&thinsp;&emsp;&emsp;"}}
          C --> D("Do you have more tokens?")
          D -- Yes --> C
          D -- No --> E("Do you want to customize your bot's CLI?")
          B -- No --> E
          E -- Yes --> F{{"&thinsp;parse_args()&ensp;&emsp;"}}
          F --> G("Is your bot simple to create and set up?")
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

??? example "Example - The Botstrap Interface"

    <div id="botstrap-example"/>
    === "Overview"
        ```{.text title="" .line-numbers-off}
        📁 workspace/
        └── 📁 examplebot/
            ├── 📄 __main__.py
            └── 📄 extras.py
        ```

        This is an extensive, multi-part example that uses the file structure outlined
        above, along with the [Pycord][1] library.

        If any of the code or console output in the following tabs is unclear, try using
        the search bar at the top of the page to look up the key terms and read through
        the relevant documentation, then come back to this example.

        (And if the docs aren't helpful, please do start a [discussion][2] about what
        could be clarified or improved!)

        ---
        The next two tabs (after this "Overview" tab) provide the contents of the
        **Python files** used in this example:

        - `__main__.py` - This file contains the entire Botstrap integration and
        exercises all of the recommended methods in this class, as well as a few other
        classes that are also part of Botstrap's [public API](../../api).
        - `extras.py` - This file represents a very small subset of the extra pieces
        that a Discord bot might have. Its purpose is simply to provide more context
        for the integration, so feel free to skip it if you don't find it useful.

        ---
        The subsequent tabs demonstrate the **CLI output** for various program flows
        and/or command-line arguments:

        - **CLI #1: Basics**
            1.  `python -m examplebot -h` :fontawesome-solid-arrow-right:
                Viewing the bot's help menu.
            2.  `python -m examplebot` :fontawesome-solid-arrow-right:
                Running the bot for the first time using the command from the help menu.
            3.  `python -m examplebot` :fontawesome-solid-arrow-right:
                Demonstrating automatic bot token decryption on subsequent runs.
        - **CLI #2: Tokens**
            1.  `python -m examplebot prod` :fontawesome-solid-arrow-right:
                Setting up a new password-protected token for production.
            2.  `python -m examplebot -t` :fontawesome-solid-arrow-right:
                Viewing existing tokens and deleting one of them.
        - **CLI #3: Options**
            1.  `python -m examplebot prod --alpha -a watching -s "you."`
                :fontawesome-solid-arrow-right: Playing with bot options in prod!
            2.  `python -m examplebot --alpha -m` :fontawesome-solid-arrow-right:
                Running the alpha bot in dev mode with mentions enabled.
            3.  `python -m examplebot --alpha -m -l 1` :fontawesome-solid-arrow-right:
                Same as above, but with the minimum log level set to 1.

        **Note:** All of these commands are run from the outermost (`workspace`)
        directory.

    === "`__main__.py`"
        ```py title=""
        {% include "../../examples/examplebot/__main__.py" %}
        ```

    === "`extras.py`"
        ```py title=""
        {% include "../../examples/examplebot/extras.py" %}
        ```

        **Note:** For more information about the contents of this file, check out these
        helpful guides about [setting up logging][3], [subclassing bots][4], and the
        [tasks extension][5]. (Those links point to the [Pycord][1] website, but the
        concepts they explain are likely useful regardless of which Discord API wrapper
        you're using.)

        [1]: https://docs.pycord.dev/
        [2]: https://github.com/nuztalgia/botstrap/discussions
        [3]: https://docs.pycord.dev/en/master/logging.html
        [4]: https://guide.pycord.dev/popular-topics/subclassing-bots/
        [5]: https://guide.pycord.dev/extensions/tasks/

    === "CLI #1: Basics"
        ```console title="1A) Viewing the bot's help menu."
        $ python -m examplebot -h
        {% include "../../examples/README.md" start="```text\n" end="```" %}
        ```

        ```console title="1B) Running the bot using the command from the help menu."
        $ python -m examplebot

        examplebot: You currently don't have a saved development bot token.
        Would you like to add one now? If so, type "yes" or "y": y

        Please enter your bot token now. It'll be hidden for security reasons.
        BOT TOKEN: ************************.******.***************************

        Your token has been successfully encrypted and saved.

        Do you want to run your bot with this token now? If so, type "yes" or "y": y

        examplebot: development: Attempting to log in to Discord...
        examplebot: development: Successfully logged in as "BotstrapBot#1234".
        ```

        ```console title="1C) No need to re-enter the bot token after initial setup!"
        $ python -m examplebot

        examplebot: development: Attempting to log in to Discord...
        examplebot: development: Successfully in as "BotstrapBot#1234".
        ```

    === "CLI #2: Tokens"
        ```console title="2A) Setting up a new password-protected token."
        $ python -m examplebot prod
        {% include "../../botstrap/internal/tokens.py" start=".py prod\n" end="```" %}
        ```

        ```console title="2B) Viewing existing tokens and deleting one of them."
        $ python -m examplebot -t
        {% include "../../botstrap/internal/argstrap.py" start="# (1)\n" end="```" %}
        ```

    === "CLI #3: Options"
        ```console title="3A) Running the alpha bot in production with a custom status."
        $ python -m examplebot prod --alpha -a watching -s "you."

        examplebot: Please enter the password to decrypt your production bot token.
        PASSWORD: ********

        examplebot: production: Attempting to log in to Discord...
        examplebot: production: Successfully logged in as "BotstrapBot#1234".

        2022-09-04 21:47:57 | I | BotstrapBot is currently watching you.
        ```

        ```console title="3B) Running the alpha bot in dev mode with mentions enabled."
        $ python -m examplebot --alpha -m

        examplebot: development: Attempting to log in to Discord...
        examplebot: development: Successfully logged in as "BotstrapBot#1234".

        2022-09-04 21:48:32 | W | BotstrapBot will ping @everyone in 10 seconds!!!
        2022-09-04 21:48:39 | W |  3...
        2022-09-04 21:48:40 | W |  2...
        2022-09-04 21:48:41 | W |  1...
        2022-09-04 21:48:42 | I | Just kidding! ^_^
        ```

        ```console title="3C) Same as above, but with the minimum log level set to 1 (debug)."
        $ python -m examplebot --alpha -m -l 1

        examplebot: development: Attempting to log in to Discord...
        examplebot: development: Successfully logged in as "BotstrapBot#1234".

        2022-09-04 21:50:48 | W | BotstrapBot will ping @everyone in 10 seconds!!!
        2022-09-04 21:50:48 | D | 10...
        2022-09-04 21:50:49 | D |  9...
        2022-09-04 21:50:50 | D |  8...
        2022-09-04 21:50:51 | D |  7...
        2022-09-04 21:50:52 | D |  6...
        2022-09-04 21:50:53 | D |  5...
        2022-09-04 21:50:54 | D |  4...
        2022-09-04 21:50:55 | W |  3...
        2022-09-04 21:50:56 | W |  2...
        2022-09-04 21:50:57 | W |  1...
        2022-09-04 21:50:58 | I | Just kidding! ^_^
        ```

<!-- prettier-ignore -->
::: botstrap.Botstrap
    options:
      show_root_heading: false
      show_root_toc_entry: false
      show_signature_annotations: false

<link rel="stylesheet" href="../../stylesheets/botstrap.css" />
