import os
from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()

client = Anthropic(api_key=os.environ["CLAUDE_API_KEY"])
response = client.messages.create(
    model="claude-haiku-5-5",
    max_tokens=32,
    messages=[{"role": "user", "content": "Reply with only: API key works!"}],
)
print(response.content[0].text)
