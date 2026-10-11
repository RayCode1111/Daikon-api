from openai import OpenAI

client = OpenAI(
    api_key="sk-testkey12345678901234567890123456789012345678",
    base_url="http://localhost:3000/v1"
)

response = client.chat.completions.create(
    model="qwen2.5-7b",
    messages=[
        {"role": "user", "content": "Hello Qwen!"}
    ],
    stream=True
)

for chunk in response:
    print(chunk.choices[0].delta.content or "", end="", flush=True)
print()