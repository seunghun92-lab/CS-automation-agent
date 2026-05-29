from dotenv import load_dotenv
import os
from openai import OpenAI

load_dotenv(dotenv_path=".env", override=True)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "안녕!"}]
)

print(response.choices[0].message.content)



