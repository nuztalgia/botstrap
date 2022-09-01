import logging
import sys

from discord import Bot
from discord.ext import tasks


def initialize_system_logging(log_level: int = logging.NOTSET) -> None:
    logging.basicConfig(
        level=(log_level := (log_level * 10) if log_level else logging.INFO),
        style="{",
        format="{asctime} | {levelname[0]} | {message}",
        datefmt="%Y-%m-%d %H:%M:%S",
        stream=sys.stdout,
    )
    logging.getLogger("discord").setLevel(log_level + 10)


class AlphaBot(Bot):
    def __init__(self, **options) -> None:
        self.log = logging.getLogger()
        self.log.info("Initializing AlphaBot instance.")
        super().__init__(**options)

    async def on_ready(self) -> None:
        activity = f"{self.activity.type.name} {self.activity.name}"
        self.log.debug(f"{self.user.name} is currently {activity}")

        if self.allowed_mentions.everyone:
            self.log.warning(f"{self.user.name} will ping @everyone in 10 seconds!!!")
            self.count_down.start()

    @tasks.loop(seconds=1, count=10)
    async def count_down(self) -> None:
        seconds_remaining = 10 - self.count_down.current_loop
        log = self.log.info if (seconds_remaining > 3) else self.log.warning
        log(f"{seconds_remaining}...".rjust(5))

    @count_down.after_loop
    async def after_count_down(self) -> None:
        self.log.info("Just kidding! ^_^")
