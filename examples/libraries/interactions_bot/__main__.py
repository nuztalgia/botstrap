from botstrap import Botstrap, CliColors, Color
from interactions import Client, ClientPresence, PresenceActivity, PresenceActivityType


def main() -> int:
    token = (
        Botstrap(
            name="interactions-bot",
            desc="A basic bot powered by interactions.py and Botstrap.",
            colors=CliColors(Color.pink),
        )
        .register_token(
            uid="dev",
            display_name=Color.yellow("development"),
            storage_directory=f"{__file__}/../../.botstrap_keys",
        )
        .retrieve_active_token()
    )

    activity = PresenceActivity(type=PresenceActivityType.LISTENING, name="/hello")
    client = Client(token=token, presence=ClientPresence(activities=[activity]))

    client.load("interactions_bot.example_extension")
    client.start()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
