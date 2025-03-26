from openai import OpenAI

client = OpenAI(api_key="sk-oivnadsfsnsebyyzqpecmafpclgnmrdkjipznvbjrxotkwhv", base_url="https://api.siliconflow.cn/v1")
response = client.chat.completions.create(
    model='deepseek-ai/DeepSeek-V2.5',
    messages=[
        {'role': 'user',
        'content': "中国大模型行业2025年将会迎来哪些机遇和挑战"}
    ],
    stream=True
)

for chunk in response:
    print(chunk.choices[0].delta.content, end='')