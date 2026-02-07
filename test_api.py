import httpx
import asyncio

async def test_analysis():
    url = "http://127.0.0.1:8000/api/analyze"
    
    # Try using a simple URL that doesn't block scrapers easily 
    # Or a URL you know contains text.
    payload = {
        "url": "https://pypistats.org/", # Just for a connectivity test
        "resume_text": "I am a Python Expert with experience in FastAPI and SQL."
    }
    
    async with httpx.AsyncClient() as client:
        try:
            print(f"Sending request to {url}...")
            response = await client.post(url, json=payload, timeout=30.0)
            
            if response.status_code == 200:
                print("✅ Success!")
                print("Result:", response.json())
            else:
                print(f"❌ Failed with status {response.status_code}")
                print("Response:", response.json())
                
        except Exception as e:
            print(f"An error occurred: {e}")

if __name__ == "__main__":
    asyncio.run(test_analysis())