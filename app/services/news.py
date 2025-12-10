import httpx
from typing import List, Dict
from config import settings

async def analyze_news(text: str, symbols: List[str]) -> Dict:
    prompt = f"""
    You are a market analyst. Return a JSON with:
        - sentiment: number between -1 and 1
        - impact: "low" | "medium" | "high"
        - horizon: "intraday" | "weeks" | "long_term"
        - reasoning: brief explanation
        - symbols: list of affected symbols
    News:
    {text}
    """
    payload = {
        "model": "llama3.1",
        "prompt": prompt,
        "stream": False,
    }

    async with httpx.AsyncClient() as client:
        r = await client.post(f"{settings.OLLAMA_API_URL}/generate", json=payload)
        r.raise_for_status()
        data = r.json()
        return data
