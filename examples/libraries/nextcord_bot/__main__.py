from botstrap import Botstrap, CliColors, Color
from nextcord import Activity, ActivityType
from nextcord.ext.commands import Bot


class NextcordBot(Bot):
    def __init__(self, **options) -> None:
        super().__init__(**options)
        self.load_extension("nextcord_bot.example_cog")

    async def on_ready(self) -> None:
        print(f"{type(self).__name__} is online and ready!")


def main() -> int:
    Botstrap(
        name="nextcord-bot",
        desc="A basic bot powered by Nextcord and Botstrap.",
        colors=CliColors(Color.pink),
    ).register_token(
        uid="dev",
        display_name=Color.yellow("development"),
        storage_directory=f"{__file__}/../../.botstrap_keys",
    ).run_bot(
        NextcordBot,
        activity=Activity(type=ActivityType.listening, name="/hello"),
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
