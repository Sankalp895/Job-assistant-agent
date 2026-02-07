import os
from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv()

class AIClient:
    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=os.getenv("OPENROUTER_API_KEY"),
            base_url="https://openrouter.ai/api/v1",
        )

    async def chat(self, prompt: str, system_prompt: str = "You are a professional career assistant."):
        try:
            response = await self.client.chat.completions.create(
                model="nvidia/nemotron-3-nano-30b-a3b:free",
                extra_headers={
                    "HTTP-Referer": "http://localhost:8000", 
                    "X-Title": "AI Job Assistant",          
                },
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.1,
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"OpenRouter Error: {str(e)}"