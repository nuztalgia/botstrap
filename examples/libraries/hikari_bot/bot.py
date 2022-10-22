import hikari


class HikariBot(hikari.GatewayBot):
    def __init__(self, token: str, **options) -> None:
        super().__init__(token, **options)
        self.subscribe(hikari.StartedEvent, self.on_started)
        self.subscribe(hikari.InteractionCreateEvent, self.on_interaction)

    async def on_started(self, _: hikari.StartedEvent) -> None:
        print(f'Successfully logged in as "{self.get_me()}".')
        print(f"{type(self).__name__} is online and ready!")
        await self.update_presence(
            activity=hikari.Activity(type=hikari.ActivityType.LISTENING, name="/hello")
        )

    async def on_interaction(self, event: hikari.InteractionCreateEvent) -> None:
        """Listen for slash commands being executed."""
        if not isinstance(event.interaction, hikari.CommandInteraction):
            return

        if event.interaction.command_name == "hello":
            await event.interaction.create_initial_response(
                hikari.ResponseType.MESSAGE_CREATE,
                f"Hello {event.interaction.member.mention}!",
                user_mentions=True,
            )
