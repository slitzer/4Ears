import os
import requests
import openai


def summarize(text: str, mode: str = "basic_summary", openai_api_key: str | None = None) -> str:
    engine = os.getenv("SUMMARIZATION_ENGINE", "openai")
    if engine == "openai":
        return summarize_openai(text, mode, openai_api_key)
    return summarize_ollama(text, mode)


def summarize_openai(text: str, mode: str, api_key: str | None = None) -> str:
    api_key = api_key or os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY not configured")
    client = openai.OpenAI(api_key=api_key)
    prompt = f"Summarize the following audio transcript in a clear and concise format ({mode}):\n\n{text}"
    response = client.chat.completions.create(
        model=os.getenv("OPENAI_MODEL", "gpt-3.5-turbo"),
        messages=[
            {"role": "system", "content": "You are a helpful AI assistant that summarizes transcripts."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.3,
    )
    return response.choices[0].message.content


def summarize_ollama(text: str, mode: str) -> str:
    payload = {
        "model": os.getenv("OLLAMA_MODEL", "mistral"),
        "prompt": f"Summarize the following transcript ({mode}):\n\n{text}",
        "stream": False,
    }
    url = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")
    response = requests.post(url, json=payload, timeout=60)
    response.raise_for_status()
    data = response.json()
    return data.get("response", "")
