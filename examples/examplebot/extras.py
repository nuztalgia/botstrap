import logging
import sys

from discord import Bot
from discord.ext import tasks


def initialize_system_logging(log_level: int) -> None:
    logging.basicConfig(
        level=log_level * 10,
        style="{",
        format="{asctime} | {levelname[0]} | {message}",
        datefmt="%Y-%m-%d %H:%M:%S",
        stream=sys.stdout,
    )
    logging.getLogger("discord").setLevel(logging.ERROR)


class AlphaBot(Bot):
    def __init__(self, **options) -> None:
        super().__init__(**options)
        self.log = logging.getLogger()

    async def on_ready(self) -> None:
        if self.activity:
            activity = f"{self.activity.type.name} {self.activity.name}"
            self.log.info(f"{self.user.name} is currently {activity}")

        if self.allowed_mentions.everyone:
            self.log.warning(f"{self.user.name} will ping @everyone in 10 seconds!!!")
            self.count_down.start()

    @tasks.loop(seconds=1, count=10)
    async def count_down(self) -> None:
        seconds_remaining = 10 - self.count_down.current_loop
        log = self.log.debug if (seconds_remaining > 3) else self.log.warning
        log(f"{seconds_remaining}...".rjust(5))

    @count_down.after_loop
    async def after_count_down(self) -> None:
        self.log.info("Just kidding! ^_^")
