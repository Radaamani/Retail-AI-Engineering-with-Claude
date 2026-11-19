import os

import gradio as gr
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()
client = Anthropic(api_key=os.environ["CLAUDE_API_KEY"])


def ask_claude(question):
    response = client.messages.create(
        model="claude-haiku-5-5",
        max_tokens=256,
        messages=[{"role": "user", "content": question}],
    )
    return response.content[0].text


if __name__ == "__main__":
    demo = gr.Interface(fn=ask_claude, inputs="textbox", outputs="textbox")
    demo.launch(server_name="127.0.0.1", share=False)
