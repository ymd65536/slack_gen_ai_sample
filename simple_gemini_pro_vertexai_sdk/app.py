import os
import re

from slack_bolt import App, Ack
from slack_bolt.adapter.socket_mode import SocketModeHandler

import vertexai
from vertexai.preview.generative_models import GenerativeModel

PROJECT_ID = os.environ.get("PROJECT_ID", "")
APP_ENVIRONMENT = os.environ.get("APP_ENVIRONMENT", "")
SLACK_BOT_TOKEN = os.environ.get("SLACK_BOT_TOKEN", "")
SLACK_APP_TOKEN = os.environ.get("SLACK_APP_TOKEN", "")
PORT = os.environ.get("PORT", 8080)
app = App(
    token=SLACK_BOT_TOKEN, process_before_response=True
)


def handle_mention(event, say):

    thread_id = event['ts']
    if "thread_ts" in event:
        thread_id = event['thread_ts']

    say("処理中", thread_ts=thread_id)

    vertexai.init(project=PROJECT_ID, location="asia-northeast1")
    use_chat_model_name = "gemini-1.0-pro"
    generation_model = GenerativeModel(use_chat_model_name)

    message = str(re.sub("<@.*>", "", event['text']))
    responses = generation_model.generate_content(
        message,
        generation_config={
            "max_output_tokens": 2048,
            "temperature": 0,
            "top_p": 1
        },
        stream=True
    )
    answer = "".join([response.text for response in responses])
    say(answer, thread_ts=thread_id)


def slack_ack(ack: Ack):
    ack()


app.event("app_mention")(ack=slack_ack, lazy=[handle_mention])


# アプリを起動します
if __name__ == "__main__":
    if APP_ENVIRONMENT == "prod":
        app.start(port=int(PORT))
    else:
        print("SocketModeHandler")
        SocketModeHandler(app, SLACK_APP_TOKEN).start()
