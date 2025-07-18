import requests
import json
import re
import traceback

def generate_xss_payloads_via_llm(context, num=5):
    api_key = "<YOUR_API_KEY>"  # Replace with your actual API key
    url = "https://openrouter.ai/api/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/your-repo",  # Update if necessary
        "X-Title": "Reflected-XSS-Filtration"
    }

    system_prompt = """You are an expert XSS payload generator. Respond only with a list of context-aware XSS payloads inside a JSON array. Respond ONLY with a single valid JSON array containing 5 XSS payloads. Do NOT include markdown, text, explanations, or multiple blocks. Format:
[
  { "payload": "..." },
  { "payload": "..." },
  ...
]
"""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Generate {num} unique XSS payloads for this context: {context}"}
    ]

    try:
        response = requests.post(url, headers=headers, json={
            "model": "mistralai/mistral-7b-instruct",
            "messages": messages,
            "temperature": 0.7
        })

        if response.status_code != 200:
            print(f"[!] API Error {response.status_code}")
            print("[!] Response text:", response.text)
            return []

        try:
            json_data = response.json()
        except Exception:
            print("[!] Response not in JSON format:")
            print(response.text)
            return []

        # Check if 'choices' field is present
        if "choices" not in json_data:
            print("[!] 'choices' field missing in API response.")
            print("[!] Full response:", json.dumps(json_data, indent=2))
            return []

        content = json_data["choices"][0]["message"]["content"].strip()

        # Try to directly parse the content
        try:
            payloads = json.loads(content)
            if isinstance(payloads, list):
                return payloads
        except Exception:
            pass  # Fallback to regex

        # Try to extract first valid JSON array using regex
        match = re.search(r"\[\s*{.*?}\s*.*?\]", content, re.DOTALL)
        if match:
            try:
                payloads = json.loads(match.group(0))
                if isinstance(payloads, list):
                    return payloads
            except Exception as e:
                print(f"[!] Regex JSON parsing failed: {e}")
                traceback.print_exc()

        print("[!] No valid JSON array could be extracted.")
        print("[!] Raw content:\n", content)
        return []

    except Exception as e:
        print(f"[!] LLM generation failed: {e}")
        traceback.print_exc()
        return []
