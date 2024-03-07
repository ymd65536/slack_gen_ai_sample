import os
import re

from slack_bolt import App, Ack
from slack_bolt.adapter.socket_mode import SocketModeHandler
from langchain_google_vertexai import VertexAI

APP_ENVIRONMENT = os.environ.get("APP_ENVIRONMENT", "")
SLACK_BOT_TOKEN = os.environ.get("SLACK_BOT_TOKEN", "")
SLACK_APP_TOKEN = os.environ.get("SLACK_APP_TOKEN", "")
PORT = os.environ.get("PORT", 8080)

app = App(
    token=SLACK_BOT_TOKEN, process_before_response=True
)


def handle_mention(event, say):
    use_chat_model_name = "gemini-pro"
    llm = VertexAI(model_name=use_chat_model_name, temperature=0)
    thread_id = event['ts']
    if "thread_ts" in event:
        thread_id = event['thread_ts']

    message = re.sub("<@.*>", "", event['text'])
    result = llm.invoke(message)
    say(str(result), thread_ts=thread_id)


def slack_ack(ack: Ack):
    ack()


app.event("app_mention")(ack=slack_ack, lazy=[handle_mention])


if __name__ == "__main__":
    if APP_ENVIRONMENT == "prod":
        app.start(port=int(PORT))
    else:
        print("SocketModeHandler")
        SocketModeHandler(app, SLACK_APP_TOKEN).start()
