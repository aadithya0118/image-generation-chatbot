# chatbot.py
import os
import requests
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

OPENAI_COMPAT_BASE = "https://generativelanguage.googleapis.com/v1beta/openai"
MODEL = "gemini-2.0-flash-exp"
client = OpenAI(base_url=OPENAI_COMPAT_BASE, api_key=GEMINI_API_KEY)


# -----------------------
# Web Search (DuckDuckGo)
# -----------------------
def web_search_duckduckgo(query: str) -> str:
    try:
        ddg_url = "https://api.duckduckgo.com/"
        response = requests.get(
            ddg_url,
            params={"q": query, "format": "json", "no_html": "1", "skip_disambig": "1"},
            timeout=8,
            headers={"User-Agent": "Mozilla/5.0"}
        )
        if response.status_code == 200:
            data = response.json()
            if data.get("Abstract"):
                return f"Source: DuckDuckGo\n\n{data['Abstract']}"
    except:
        return None
    return None


# -----------------------
# Wikipedia Search
# -----------------------
def web_search_wikipedia(query: str) -> str:
    try:
        wiki_query = query.replace(" ", "_").strip()
        response = requests.get(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{wiki_query}",
            timeout=8,
            headers={"User-Agent": "Mozilla/5.0"}
        )
        if response.status_code == 200:
            data = response.json()
            extract = data.get("extract", "")
            if extract:
                return f"Source: Wikipedia\n\n{extract}"
    except:
        return None
    return None


# -----------------------
# Combined Search
# -----------------------
def web_search_combined(query: str) -> str:
    ddg = web_search_duckduckgo(query)
    if ddg:
        return ddg
    wiki = web_search_wikipedia(query)
    if wiki:
        return wiki
    return f"No web data found. Using AI knowledge for: {query}"


# -----------------------
# Image Generation (Pollinations)
# -----------------------
def generate_image_with_pollinations(prompt: str) -> bytes:
    try:
        enhanced_prompt = f"{prompt.strip()}, high quality, detailed, professional"
        encoded_prompt = requests.utils.quote(enhanced_prompt)
        url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=1024&model=flux"
        response = requests.get(url, timeout=30)
        if response.status_code == 200:
            return response.content
    except Exception as e:
        print(f"Image generation error: {e}")
    return None


# -----------------------
# Gemini Answer
# -----------------------
def ask_gemini_for_answer(query: str, context: str) -> tuple[str, str]:
    needs_image = any(word in query.lower() for word in [
        "image", "picture", "photo", "show me", "diagram", "draw"
    ])

    system_prompt = """
   You are imagine chatbot 🤖, a friendly and funny too.
    You can:
      - Answer questions clearly.
      - Generate creative images when asked.
      - Make jokes or be humorous sometimes.
    Always be helpful, cheerful, and creative.
    """

    try:
        resp = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Q: {query}\n\nContext:\n{context}"}
            ],
            temperature=0.3,
            max_tokens=2000,
        )
        answer = resp.choices[0].message.content.strip()
        image_prompt = query if needs_image else ""
        return answer, image_prompt
    except Exception as e:
        return f"Error: {e}", ""
