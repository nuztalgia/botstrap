from nextcord import Interaction, slash_command
from nextcord.ext.commands import Bot, Cog


class Example(Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    @slash_command(description="Say hello.")
    async def hello(self, interaction: Interaction) -> None:
        await interaction.response.send_message(f"Hello {interaction.user.mention}!")


def setup(bot: Bot) -> None:
    bot.add_cog(Example(bot))
