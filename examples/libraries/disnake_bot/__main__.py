from botstrap import Botstrap, CliColors, Color
from disnake import Activity, ActivityType
from disnake.ext.commands import InteractionBot


class DisnakeBot(InteractionBot):
    def __init__(self, **options) -> None:
        super().__init__(**options)
        self.load_extension("disnake_bot.example_cog")

    async def on_ready(self) -> None:
        print(f"{type(self).__name__} is online and ready!")


def main() -> int:
    Botstrap(
        name="disnake-bot",
        desc="A basic bot powered by disnake and Botstrap.",
        colors=CliColors(Color.pink),
    ).register_token(
        uid="dev",
        display_name=Color.yellow("development"),
        storage_directory=f"{__file__}/../../.botstrap_keys",
    ).run_bot(
        DisnakeBot,
        activity=Activity(type=ActivityType.listening, name="/hello"),
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
