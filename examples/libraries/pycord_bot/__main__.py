from botstrap import Botstrap, CliColors, Color
from discord import Activity, ActivityType, Bot


class PycordBot(Bot):
    def __init__(self, **options) -> None:
        super().__init__(**options)
        self.load_extension("pycord_bot.example_cog")

    async def on_ready(self) -> None:
        print(f"{type(self).__name__} is online and ready!")


def main() -> int:
    Botstrap(
        name="pycord-bot",
        desc="A basic bot powered by Pycord and Botstrap.",
        colors=CliColors(Color.pink),
    ).register_token(
        uid="dev",
        display_name=Color.yellow("development"),
        storage_directory=f"{__file__}/../../.botstrap_keys",
    ).run_bot(
        PycordBot,
        activity=Activity(type=ActivityType.listening, name="/hello"),
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
