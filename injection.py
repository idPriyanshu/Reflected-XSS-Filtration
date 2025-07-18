import json
import requests
from urllib.parse import urlencode
from bs4 import BeautifulSoup
import re

# Load payloads and request template
with open("payloads.txt", "r", encoding="utf-8") as f:
    payloads = [line.strip() for line in f if line.strip()]

with open("request.json", "r", encoding="utf-8") as f:
    request_data = json.load(f)

results = []

def check_live_reflection(html: str, payload: str) -> str:
    """
    Parses HTML to determine if and how the payload is reflected in the DOM.
    Returns the reflection type: 'script', 'attribute', 'innerHTML', or 'not reflected'.
    """
    soup = BeautifulSoup(html, "html.parser")

    # Check script block
    for script in soup.find_all("script"):
        if payload in script.text:
            return "script"

    # Check attributes
    for tag in soup.find_all(True):
        for attr_value in tag.attrs.values():
            if isinstance(attr_value, str) and payload in attr_value:
                return "attribute"
            if isinstance(attr_value, list) and any(payload in v for v in attr_value):
                return "attribute"

    # Check inner text or HTML content
    if payload in soup.get_text() or payload in str(soup):
        return "innerHTML"

    return "not reflected"

# Run tests
for request_template in request_data:
    for payload in payloads:
        mutated_request = json.loads(json.dumps(request_template))  # deep copy
        method = mutated_request.get("method", "GET").upper()
        url = mutated_request["url"]
        headers = mutated_request.get("headers", {})
        body = mutated_request.get("body", "")

        if method == "GET":
            full_url = url.replace("{{xss_test}}", payload)
            resp = requests.get(full_url, headers=headers)
        else:
            full_body = body.replace("{{xss_test}}", payload)
            data_dict = dict(param.split("=") for param in full_body.split("&") if "=" in param)
            encoded_body = urlencode(data_dict)
            resp = requests.post(url, headers=headers, data=encoded_body)

        content = resp.text
        reflection_type = check_live_reflection(content, payload)

        result = {
            "payload": payload,
            "url": url,
            "method": method,
            "status_code": resp.status_code,
            "reflected": reflection_type != "not reflected",
            "reflection_type": reflection_type,
        }

        results.append(result)


# Save results
with open("results.txt", "w", encoding="utf-8") as f:
    for r in results:
        f.write(json.dumps(r, indent=2) + "\n")
