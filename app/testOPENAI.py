from openai import OpenAI

with open("openAI_apiKey.txt", "r") as file:
    api_key = file.read().strip()

client = OpenAI(api_key=api_key)
completion = client.chat.completions.create(
    model="gpt-4o",
    store=True,
    messages=[
        {"role": "user", "content": "write a haiku about ai"}
    ]
)

