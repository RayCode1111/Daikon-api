# from openai import OpenAI

# client = OpenAI(
#     api_key="sk-b453c72e38b44ab0b5bf9b5eb3d8be3c3c3a3d05abca2d2e2ecec0c876c456b1",
#     base_url="http://localhost:3000/v1"  # Or your public tunnel URL
# )

# response = client.chat.completions.create(
#     model="qwen2.5-7b",
#     messages=[
#         {"role": "user", "content": "Tell me about the story of the OpenAI company in 500 words."}
#     ],
#     stream=True  # Supports real-time streaming
# )

# for chunk in response:
#     if chunk.choices:
#         content = chunk.choices[0].delta.content or ""
#         print(content, end="", flush=True)
    
# print()





# from openai import OpenAI

# client = OpenAI(
#     api_key="sk-FDGdANwoZ99gEqiatv9rhigLoTl1PfrxLQJiHMu2dsnmipEG",
#     base_url="https://daikon-api.onrender.com/v1"
# )

# response = client.chat.completions.create(
#     model="qwen2.5-7b",
#     messages=[
#         {"role": "system", "content": "You are a helpful coding assistant."},
#         {"role": "user", "content": "Write a Python function to check if a string is a palindrome."}
#     ],
#     temperature=0.7,
# )

# print(response.choices[0].message.content)






from openai import OpenAI

client = OpenAI(
    api_key="sk-FDGdANwoZ99gEqiatv9rhigLoTl1PfrxLQJiHMu2dsnmipEG",
    base_url="https://daikon-api.onrender.com/v1"
)

stream = client.chat.completions.create(
    model="Qwen/Qwen2.5-7B-Instruct-AWQ",
    messages=[{"role": "user", "content": "Explain quantum computing in 3 bullets."}],
    stream=True,
)

for chunk in stream:
    if chunk.choices[0].delta.content is not None:
        print(chunk.choices[0].delta.content, end="", flush=True)
print()