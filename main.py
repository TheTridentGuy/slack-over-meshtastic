import meshtastic.serial_interface
from pubsub import pub
import dotenv
import os
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler


dotenv.load_dotenv()
slack_app = App(token=os.environ["SLACK_BOT_TOKEN"])


def on_receive(packet, interface):
    print(packet, interface)


meshtastic_interface = meshtastic.serial_interface.SerialInterface()
pub.subscribe(on_receive, "meshtastic.receive")


if __name__ == "__main__":
    try:
        SocketModeHandler(slack_app, os.environ["SLACK_APP_TOKEN"]).start()
    except KeyboardInterrupt:
        meshtastic_interface.close()
