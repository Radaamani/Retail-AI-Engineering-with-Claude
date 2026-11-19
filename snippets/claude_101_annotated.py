import os
import dotenv
import anthropic

# Loading private key to authenticate to the model service provider. 
# Keep key in .env , not check in git. There is a lot of attack to extract keys. Because once found out millions of dollars worth is can be spent by attackers
dotenv.load_dotenv(".env")

# Intializing client. Request to this uses  their compute to run AI Model and return response to you
client = anthropic.Anthropic(api_key=os.environ["CLAUDE_API_KEY"])

# Current list of available models
print(client.models.list())  # List available models

# Sending a message to ask AI Model, which will reply
response = client.messages.create(
    model    = "claude-haiku-5-5",
    max_tokens = 1024,
    messages = [
            {
                "role": "user", 
                "content": "What is summary of AI"
            },
            {
                "role": "user", 
                "content": "What is 2 + 3?"
            },
            {
                "role": "user", "content": "Reverse following words: 'Hello World'"
            },
    ]
)

# Important parameters of clients.messages.create()
# model: which model to use. Here we are using claude-haiku-5-5, which is a small model. There are other models available, which can be listed by client.models.list()
# messages: list of messages to send to the model. Each message is a dict with role and content. Role can be user, assistant, or system. Content is the text of the message.
# max_tokens: maximum number of tokens to generate in the response. 
# tools: List of callable functions that the model can call if needed. tools = API calls of AI Models
# mcp_servers: list of servers. Each servers have callable functions that model can call if needed. MCP = Model Context Protocol = Model Tool Calling Protocol. 
# container: Contains list of skills in json format {"skill_id": <id>, "type": ["anthropic" , "custom"]]}


print(response.content[0].text)