import os

import gradio as gr
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()
client = Anthropic(api_key=os.environ["CLAUDE_API_KEY"])
model = os.getenv("CLAUDE_MODEL", "claude-haiku-5-5")


def reply(message, history):
    messages = []
    for earlier_message in history:
        role = earlier_message["role"]
        content = earlier_message["content"]
        messages.append({"role": role, "content": content})

    messages.append({"role": "user", "content": message})

    response = client.messages.create(
        model=model, max_tokens=512, messages=messages,
    )
    text = []
    for block in response.content:
        if block.type == "text":
            text.append(block.text)
    return "\n".join(text) or "Claude returned no text."


if __name__ == "__main__":
    chat = gr.ChatInterface(reply, title="Claude chatbot")
    chat.launch(server_name="127.0.0.1", share=False)
