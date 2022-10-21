import interactions


class Example(interactions.Extension):
    def __init__(self, client: interactions.Client) -> None:
        self.client = client

    @interactions.extension_listener
    async def on_ready(self) -> None:
        print(f"{self.client.me.name} is online and ready!")

    @interactions.extension_command(description="Say hello.")
    async def hello(self, ctx: interactions.CommandContext) -> None:
        await ctx.send(f"Hello {ctx.author.mention}!")


def setup(client: interactions.Client) -> None:
    Example(client)
