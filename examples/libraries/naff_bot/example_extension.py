from naff import Client, Extension, InteractionContext, slash_command


class Example(Extension):
    def __init__(self, bot: Client) -> None:
        self.bot = bot

    @slash_command(name="hello", description="Say hello.")
    async def hello(self, ctx: InteractionContext) -> None:
        await ctx.send(f"Hello {ctx.author.mention}!")


def setup(bot: Client) -> None:
    Example(bot)
