from openai import OpenAI

from backend.app.core.config import settings

client = OpenAI(
    base_url="https://router.huggingface.co/v1",
    api_key=settings.HUGGING_FACE_API_KEY,
)

completion = client.chat.completions.create(
    model="moonshotai/Kimi-K2-Instruct-0905",
    messages=[
        {
            "role": "user",
            "content": "Generate a poem about the sea."
        }
    ],
)

print(completion.choices[0].message)