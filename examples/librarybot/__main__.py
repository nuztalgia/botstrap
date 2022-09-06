from botstrap import Botstrap, CliColors, Color, Option
from librarybot.libraries import create_bot, get_discord_packages, get_library_names


botstrap = Botstrap(name="librarybot", colors=CliColors(Color.green))

if not (installed_pkgs := get_discord_packages()):
    botstrap.exit_process("\nNone of the supported Discord libraries are installed.")

custom_options = {}
default_pkg = installed_pkgs[0]

# If multiple Discord libs are installed, provide a CLI option to select the one to use.
if len(installed_pkgs) > 1:
    custom_options["library"] = Option(
        default=default_pkg,
        choices=installed_pkgs,
        help="The name of the Discord library to use to run the bot.",
    )

selected_pkg = vars(botstrap.parse_args(**custom_options)).get("library", default_pkg)

# Tap into Botstrap's underlying infrastructure to print nicely-formatted console text.
if len(lib_names := get_library_names(selected_pkg)) != 1:
    botstrap.exit_process(
        f'\nAmbiguous package name: "{selected_pkg}" matches libraries '
        f"{(s := botstrap.strings).join_choices(lib_names, conjunction=s.m_conj_and)}."
    )
botstrap.print_prefixed(f"Running bot using the '{Color.cyan(lib_names[0])}' library.")

match selected_pkg:
    case "disnake":
        botstrap.run_bot("disnake.ext.commands.InteractionBot")
    case "hikari":
        create_bot("hikari.GatewayBot", token=botstrap.retrieve_active_token()).run()
    case "interactions":
        bot = create_bot("interactions.Client", token=botstrap.retrieve_active_token())
        bot.start()
    case "naff":
        create_bot("naff.Client").start(botstrap.retrieve_active_token())
    case "nextcord":
        botstrap.run_bot("nextcord.ext.commands.Bot")
    case _:
        # Selected package is discord.py or Pycord. These work with Botstrap by default.
        botstrap.run_bot()
