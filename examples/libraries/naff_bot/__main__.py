from botstrap import Botstrap, CliColors, Color
from naff import Activity, ActivityType, Client, listen


class NaffBot(Client):
    def __init__(self, **options) -> None:
        super().__init__(**options)
        self.load_extension("naff_bot.example_extension")

    @listen()
    async def on_startup(self) -> None:
        print(f'Successfully logged in as "{self.user}".')
        print(f"{type(self).__name__} is online and ready!")


def main() -> int:
    Botstrap(
        name="naff-bot",
        desc="A basic bot powered by NAFF and Botstrap.",
        colors=CliColors(Color.pink),
    ).register_token(
        uid="dev",
        display_name=Color.yellow("development"),
        storage_directory=f"{__file__}/../../.botstrap_keys",
    ).run_bot(
        NaffBot,
        run_method_name="start",
        activity=Activity.create(type=ActivityType.LISTENING, name="/hello"),
        sync_interactions=True,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
