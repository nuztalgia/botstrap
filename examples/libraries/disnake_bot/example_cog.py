from disnake import ApplicationCommandInteraction
from disnake.ext.commands import Bot, Cog, slash_command


class Example(Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    @slash_command(description="Say hello.")
    async def hello(self, interaction: ApplicationCommandInteraction) -> None:
        await interaction.response.send_message(f"Hello {interaction.author.mention}!")


def setup(bot: Bot) -> None:
    bot.add_cog(Example(bot))
