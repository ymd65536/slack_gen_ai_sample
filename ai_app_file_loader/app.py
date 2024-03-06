import os
import re

from slack_bolt import App, Ack
from slack_bolt.adapter.socket_mode import SocketModeHandler

from langchain_community.document_loaders import DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

from langchain_google_vertexai import VertexAI
from langchain_google_vertexai import VertexAIEmbeddings
from langchain.indexes import VectorstoreIndexCreator
from langchain_community.vectorstores import FAISS

project_id = os.environ.get("PROJECT_ID", "")
APP_ENVIRONMENT = os.environ.get("APP_ENVIRONMENT", "")
SLACK_BOT_TOKEN = os.environ.get("SLACK_BOT_TOKEN", "")
SLACK_APP_TOKEN = os.environ.get("SLACK_APP_TOKEN", "")
PORT = os.environ.get("PORT", 8080)
app = App(
    token=SLACK_BOT_TOKEN,
    process_before_response=True
)


def document_loader():
    loader = DirectoryLoader('./', glob="**/README.md")
    return loader.load()


def text_splitter(docs, chunk_size=1000, chunk_overlap=100, separators=["。"]):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=separators
    )

    split_text = []

    for doc in docs:
        if len(doc.page_content) > chunk_size:
            split_text.extend(text_splitter.split_documents(docs))
        else:
            split_text.extend(doc)

    return split_text


def query(query, documents):
    embeddings = VertexAIEmbeddings(model_name="textembedding-gecko@001")
    index = VectorstoreIndexCreator(
        embedding=embeddings,
        vectorstore_cls=FAISS
    ).from_documents(documents)

    chat = VertexAI(model_name="gemini-1.0-pro-001", temperature=0)
    result = index.query_with_sources(query, llm=chat)

    return result


def handle_mention(event, say):
    print("handle_mention")
    thread_id = event['ts']

    if "thread_ts" in event:
        thread_id = event['thread_ts']

    docs = document_loader()
    split_text = text_splitter(docs)

    user_query = event.get('text', "")
    message = re.sub("<@.*>", "", user_query) + " in Japanese"
    res = query(query=message, documents=split_text)

    answer = res['answer']
    sources = res['sources']

    result = f"""
回答：
{answer}
参照元：
{sources}
"""
    
    say(result, thread_ts=thread_id)


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
