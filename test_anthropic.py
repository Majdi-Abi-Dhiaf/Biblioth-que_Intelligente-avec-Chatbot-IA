import json
import urllib.request
import urllib.error


GROQ_MODEL   = "llama-3.3-70b-versatile"
GROQ_URL     = "https://api.groq.com/openai/v1/chat/completions"

payload = json.dumps({
    "model": GROQ_MODEL,
    "messages": [
        {"role": "user", "content": "Réponds en français: Bonjour, est-ce que l'API Groq fonctionne ?"}
    ],
    "max_tokens": 200,
}).encode("utf-8")

req = urllib.request.Request(
    GROQ_URL,
    data=payload,
    headers={
        "Content-Type":  "application/json",
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json",
    },
    method="POST"
)

try:
    with urllib.request.urlopen(req, timeout=20) as resp:
        data = json.loads(resp.read())
        print(data["choices"][0]["message"]["content"])

except urllib.error.HTTPError as e:
    print("HTTP Error:", e.code)
    print(e.read().decode("utf-8"))

except Exception as e:
    print("Error:", e)
