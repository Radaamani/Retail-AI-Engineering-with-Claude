from litellm import completion
import os

os.environ["ANTHROPIC_API_KEY"] = "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"

response = completion(
  model="anthropic/claude-haiku-5-5",
  messages=[{"role": "user", "content": "Hello, how are you?"}]
)
print(response.choices[0].message.content)

from litellm import completion, completion_cost
cost = completion_cost(completion_response=response)
formatted_string = f"${float(cost):.10f}"
print(formatted_string)