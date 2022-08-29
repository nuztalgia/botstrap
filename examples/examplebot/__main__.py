from . import extras
from botstrap import Botstrap, CliColors, Color, Option
from discord import AllowedMentions


botstrap = (
    Botstrap(name="examplebot", colors=CliColors(Color.pink))
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
