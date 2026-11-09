import os

import dotenv
import meshtastic.serial_interface
from pubsub import pub
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

dotenv.load_dotenv()
SLACK_CHANNEL = os.environ["SLACK_CHANNEL"]
MESHTASTIC_CHANNEL_INDEX = int(os.environ["MESHTASTIC_CHANNEL_INDEX"])
slack_app = App(token=os.environ["SLACK_BOT_TOKEN"])
slack_client = slack_app.client


def on_receive(packet, interface):
    if packet.get("decoded", {}).get("portnum") == "TEXT_MESSAGE_APP":
        from_node = interface.nodesByNum[packet["from"]]
        blocks = [
            {
                "type": "section",
                "text": {
                    "type": "plain_text",
                    "text": packet["decoded"]["text"],
                    "emoji": True
                }
            }
        ]
        slack_client.chat_postMessage(channel=SLACK_CHANNEL, text=packet["decoded"]["text"], blocks=blocks,
                                      username=f"[{from_node["user"]["shortName"]}] {from_node["user"]["longName"]}")


@slack_app.event("message")
def on_slack_message(message):
    if message["channel"] == SLACK_CHANNEL and (text := message.get("text")):
        meshtastic_interface.sendText(text, channelIndex=MESHTASTIC_CHANNEL_INDEX)


meshtastic_interface = meshtastic.serial_interface.SerialInterface()
pub.subscribe(on_receive, "meshtastic.receive")

if __name__ == "__main__":
    try:
        SocketModeHandler(slack_app, os.environ["SLACK_APP_TOKEN"]).start()
    except KeyboardInterrupt:
        meshtastic_interface.close()
