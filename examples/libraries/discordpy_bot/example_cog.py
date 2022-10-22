from discord import Interaction
from discord.app_commands import command
from discord.ext.commands import Bot, Cog


class Example(Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    @command(description="Say hello.")
    async def hello(self, interaction: Interaction) -> None:
        await interaction.response.send_message(f"Hello {interaction.user.mention}!")


async def setup(bot: Bot) -> None:
    await bot.add_cog(Example(bot))
