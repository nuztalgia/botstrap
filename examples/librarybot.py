from botstrap import Botstrap, CliColors, Color, Option

# A mapping of supported Discord library names to the names of their bot classes.
bot_classes = {
    "discordpy": "discord.Client",
    "disnake": "disnake.ext.commands.InteractionBot",
    "hikari": "hikari.GatewayBot",
    "interactions": "interactions.Client",
    "naff": "naff.Client",
    "nextcord": "nextcord.ext.commands.Bot",
    "pycord": "discord.Bot",
}

# Initialize the Botstrap integration and use it to parse command-line arguments.
botstrap = Botstrap(name="librarybot", colors=CliColors(Color.green))
args = botstrap.parse_args(
    library=Option(
        choices=bot_classes.keys(),
        help="The name of the Discord library to use to run the bot.",
    )
)

if not args.library:
    # If a library was not explicitly specified, let the default behavior do its thing.
    botstrap.run_bot()
else:
    # Otherwise, announce the selected library and run the bot with appropriate params.
    botstrap.print_prefixed(
        f"Running bot using the '{Color.cyan(args.library)}' library."
    )
    run_method_name = "start" if args.library in ("interactions", "naff") else "run"
    init_with_token = args.library in ("hikari", "interactions")
    try:
        botstrap.run_bot(
            bot_class=bot_classes[args.library],
            run_method_name=run_method_name,
            init_with_token=init_with_token,
        )
    except ImportError:
        botstrap.print_prefixed(
            Color.red(f"'{args.library}' is not installed!\n"), is_error=True
        )
