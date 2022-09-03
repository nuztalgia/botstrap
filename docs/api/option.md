<!-- prettier-ignore -->
::: botstrap.Option
    options:
      filters:
        - "^[a-z]"
      heading_level: 1
      show_category_heading: true

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
        ```py title="example.py" hl_lines="12"
        from botstrap import Botstrap, Option

        args = Botstrap().parse_args(
            message=Option(),
            reply_chance=Option(default=0.01),
            ping_on_reply=Option(flag=True),
            daily_limit=Option(default=10, choices=range(-1, 101)),
        )
        print(f"\nargs as 'Results':\n    {args}")
        print(f"args as a 'dict':\n    {(args_dict := vars(args))}\n")

        if args.message and args.daily_limit and (chance := max(0, min(args.reply_chance, 1))):
            print("> Random replies are enabled.")
            print(f"   - {int(chance * 100)}% chance of replying with '{args.message}'.")
            print(f"   - Will{'' if args.ping_on_reply else ' not'} ping the original sender.")
            if args.daily_limit > 0:
                print(f"   - This will occur a maximum of {args.daily_limit} times per day.")
        else:
            print("> Random replies are disabled.")
        ```

        For reference, here's how the `#!py if` condition on line `12` (highlighted
        above) can be equivalently written using a `#!py dict`:

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

        $ python example.py -m "hello, friend" -d -1 -p
        args as 'Results':
            Results(message='hello, friend', reply_chance=0.01, ping_on_reply=True, daily_limit=-1)
        args as a 'dict':
            {'message': 'hello, friend', 'reply_chance': 0.01, 'ping_on_reply': True, 'daily_limit': -1}

        > Random replies are enabled.
           - 1% chance of replying with 'hello, friend'.
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
<script src="../../javascripts/option.js"></script>
