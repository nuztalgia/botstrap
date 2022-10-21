from discord import ApplicationContext, Bot, Cog, slash_command


class Example(Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    @slash_command(description="Say hello.")
    async def hello(self, ctx: ApplicationContext) -> None:
        await ctx.respond(f"Hello {ctx.author.mention}!")


def setup(bot: Bot) -> None:
    bot.add_cog(Example(bot))
