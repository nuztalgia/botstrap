from botstrap import Botstrap, CliColors, Color


def main() -> int:
    Botstrap(
        name="hikari-bot",
        desc="A basic bot powered by hikari and Botstrap.",
        colors=CliColors(Color.pink),
    ).register_token(
        uid="dev",
        display_name=Color.yellow("development"),
        storage_directory=f"{__file__}/../../.botstrap_keys",
    ).run_bot(
        "hikari_bot.bot.HikariBot",
        init_with_token=True,
        banner=None,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
