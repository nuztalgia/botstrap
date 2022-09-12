<!-- prettier-ignore -->
::: botstrap.Option
    options:
      heading_level: 1
      members: false

??? abstract "Diagram - Defining an Option"

    Although it's possible to instantiate this class without specifying any custom
    field values, it's almost always ideal to tailor them to better fit your bot's
    requirements. However, some fields are mutually exclusive. :crossed_swords:

    This diagram helps to illustrate which fields should (and shouldn't) be set when
    defining an option. Start at the top, and click on each field name that you
    encounter on the way down for more details about how to customize its value.

    <figure markdown>
      ```mermaid
      flowchart TB
          A("What is the value type of the option?")
          A -- bool --> B{{"&thinsp;flag&thinsp;&thinsp;&emsp;"}}
          A -- str --> C{{"&thinsp;default&ensp;&emsp;"}}
          A -- int --> C
          A -- float --> C
          B --> F{{"&thinsp;help&emsp;"}}
          C --> D("Is there a restricted set of values?")
          D -- Yes --> E{{"&thinsp;choices&emsp;"}}
          D -- No --> F
          E --> F
          F --> G(("Done!"))

          click B "#botstrap.options.Option.flag"
          click C "#botstrap.options.Option.default"
          click E "#botstrap.options.Option.choices"
          click F "#botstrap.options.Option.help"

          class B,C,E,F field;
          classDef field font-family: Roboto Mono, font-size: 14px, font-weight: bold
          classDef field fill: #7c4dff66, stroke: #7c4dffff, stroke-width: 2px

          class A,D textBox;
          classDef textBox fill: #00b0ff11, stroke: #00b0ff33, stroke-width: 2px

          class G lastNode;
          classDef lastNode fill: #00c85366, stroke: #00c853cc
          classDef lastNode font-weight: bold, stroke-width: 2px

          linkStyle 1,2,3,6 opacity: 0.9, stroke-dasharray: 8 4
          linkStyle 0,7 opacity: 0.9, stroke-dasharray: 5 6
          linkStyle 4,5,8,9 opacity: 0.9, stroke-width: 2px
      ```
    </figure>

<!-- prettier-ignore -->
::: botstrap.Option
    options:
      filters:
        - "^[a-z]"
      show_category_heading: true
      show_root_heading: false
      show_root_toc_entry: false

## Constants

<!-- prettier-ignore -->
::: botstrap.Option.HIDE_HELP
    options:
      heading_level: 3

## Nested Classes

<!-- prettier-ignore -->
::: botstrap.Option.Results
    options:
      heading_level: 3
      members: false

??? example "Example - Viewing and using parsed option values"

    === "Python Code"
        ```{.py title="example.py" hl_lines="12" .annotate}
        from botstrap import Botstrap, Option

        args = Botstrap().parse_args(
            message=Option(),
            reply_chance=Option(default=0.01),
            ping_on_reply=Option(flag=True),
            daily_limit=Option(default=10, choices=range(-1, 101)),
        )
        print(f"args as 'Results':\n  {args}") # (1)
        print(f"args as a 'dict':\n  {(args_dict := vars(args))}\n")

        if args.message and args.daily_limit and (chance := max(0, min(args.reply_chance, 1))):
            print("> Random replies are enabled.")
            print(f"  - {int(chance * 100)}% chance of replying with '{args.message}'.")
            print(f"  - Will{'' if args.ping_on_reply else ' not'} ping the original sender.")
            if args.daily_limit > 0:
                print(f"  - This will occur a maximum of {args.daily_limit} times per day.")
        else:
            print("> Random replies are disabled.")
        ```

        1.  **Note:** `args` is an instance of `Option.Results`. The following line
            creates `args_dict`, which is a `dict[str, bool | str | int | float]`.

        For reference, here's how the `if` condition on line 12 (highlighted above) can
        be equivalently written using a `dict`:

        ```{.py .line-numbers-off title=""}
        if (
            args_dict["message"]
            and args_dict["daily_limit"]
            and (chance := max(0, min(args_dict["reply_chance"], 1)))
        ):
        ```

    === "Console Output"
        ```console title="Console Session"
        $ python example.py
        args as 'Results':
          Results(message='', reply_chance=0.01, ping_on_reply=False, daily_limit=10)
        args as a 'dict':
          {'message': '', 'reply_chance': 0.01, 'ping_on_reply': False, 'daily_limit': 10}

        > Random replies are disabled.

        $ python example.py -m "hi, friend!" -d -1 -p
        args as 'Results':
          Results(message='hi, friend!', reply_chance=0.01, ping_on_reply=True, daily_limit=-1)
        args as a 'dict':
          {'message': 'hi, friend!', 'reply_chance': 0.01, 'ping_on_reply': True, 'daily_limit': -1}

        > Random replies are enabled.
          - 1% chance of replying with 'hi, friend!'.
          - Will ping the original sender.

        $ python example.py -m "cool story" -r 0.03 -d 100
        args as 'Results':
          Results(message='cool story', reply_chance=0.03, ping_on_reply=False, daily_limit=100)
        args as a 'dict':
          {'message': 'cool story', 'reply_chance': 0.03, 'ping_on_reply': False, 'daily_limit': 100}

        > Random replies are enabled.
          - 3% chance of replying with 'cool story'.
          - Will not ping the original sender.
          - This will occur a maximum of 100 times per day.
        ```

<link rel="stylesheet" href="../../stylesheets/option.css" />
