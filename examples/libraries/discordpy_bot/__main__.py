from botstrap import Botstrap, CliColors, Color
from discord import Activity, ActivityType, Intents
from discord.ext.commands import Bot


class DiscordpyBot(Bot):
    async def setup_hook(self) -> None:
        await self.load_extension("discordpy_bot.example_cog")

    async def on_ready(self) -> None:
        print(f"{type(self).__name__} is online and ready!")


def main() -> int:
    Botstrap(
        name="discordpy-bot",
        desc="A basic bot powered by discord.py and Botstrap.",
        colors=CliColors(Color.pink),
    ).register_token(
        uid="dev",
        display_name=Color.yellow("development"),
        storage_directory=f"{__file__}/../../.botstrap_keys",
    ).run_bot(
        DiscordpyBot,
        command_prefix="/",
        intents=Intents.default(),
        activity=Activity(type=ActivityType.listening, name="/hello"),
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
