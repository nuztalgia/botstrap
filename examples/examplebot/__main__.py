from botstrap import Botstrap, CliColors, Color, Option
from discord import Activity, ActivityType, AllowedMentions
from examplebot.extras import AlphaBot, initialize_system_logging


botstrap = (
    Botstrap(
        name="examplebot",
        desc="A really cool Discord bot that uses Botstrap!",
        colors=CliColors(primary=Color.pink),
    )
    .register_token("dev", display_name=Color.yellow("development"))
    .register_token(
        uid="prod",
        requires_password=True,
        display_name=Color.green("production"),
    )
)

args = botstrap.parse_args(
    loglevel=Option(
        default=2,
        choices=range(1, 5),
        help="A value from 1 to 4 specifying the minimum log level.",
    ),
    status=Option(default="", help="Text to show in the bot's Discord profile status."),
    activity=Option(
        default="playing",
        choices=("streaming", "listening", "watching"),
        help="The text preceding '--status'. Defaults to '%(default)s'.",
    ),
    mentions=Option(flag=True, help="Allow the bot to @mention members and/or roles."),
    alpha=Option(flag=True, help=Option.HIDE_HELP),
)

initialize_system_logging(log_level=args.loglevel)

activity = (
    Activity(type=getattr(ActivityType, args.activity.lower()), name=args.status)
    if args.status
    else None
)
allowed_mentions = AllowedMentions.all() if args.mentions else AllowedMentions.none()

bot_class: str | type = AlphaBot if args.alpha else "discord.Bot"
botstrap.run_bot(bot_class, activity=activity, allowed_mentions=allowed_mentions)
