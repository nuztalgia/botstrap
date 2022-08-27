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
    === "\_\_main\_\_.py"
        ```py
        from botstrap import Botstrap, CliColors, Color, Option
        from discord import AllowedMentions
        from examplebot import extras

        botstrap = (
            Botstrap(name="example-bot", colors=CliColors(Color.pink))
            .register_token(
                uid="dev",
                display_name=Color.yellow("development"),
            )
            .register_token(
                uid="prod",
                requires_password=True,
                display_name=Color.green("production"),
            )
        )

        args = botstrap.parse_args(
            description="A really cool Discord bot that uses Botstrap!",
            ll=Option(
                default="i",
                choices=("d", "debug", "i", "info", "w", "warning", "e", "error"),
                help="The lowest message level to log.",
            ),
            alpha=Option(flag=True, help="Enable features that are currently in alpha."),
            allow_pings=Option(flag=True, help="Allow the bot to ping people/roles."),
        )

        extras.initialize_logging(log_level=args.ll)

        bot_class = extras.AlphaBot if args.alpha else "discord.Bot"
        pings = AllowedMentions.everyone() if args.allow_pings else AllowedMentions.none()

        botstrap.run_bot(bot_class, allowed_mentions=pings)
        ```

    === "--help"
        ```console
        $ python -m examplebot -h
        usage: examplebot [-l <str>] [-a] [--allow-pings] [-t] [--help] [<token id>]

          A really cool Discord bot that uses Botstrap!
          Run "python -m examplebot" with no parameters to start the bot in development mode.

        positional arguments:
          <token id>            The ID of the token to use to run the bot.
                                Valid options are "dev" and "prod".

        options:
          -l <str>, --ll <str>  The lowest message level to log.
          -a, --alpha           Enable features that are currently in alpha.
          --allow-pings         Allow the bot to ping people/roles.
          -t, --tokens          View/manage your saved Discord bot tokens.
          -h, --help            Display this help message.
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
