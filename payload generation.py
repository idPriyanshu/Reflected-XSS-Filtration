import json
import urllib.parse
import os

# Import LLM-based payload generator
from llm_payloads import generate_xss_payloads_via_llm

# Load requests from JSON file
def load_requests(filename):
    if not os.path.exists(filename):
        print(f"[!] File {filename} not found.")
        return []
    
    with open(filename, 'r') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError as e:
            print(f"[!] JSON decode error: {e}")
            return []

# Inject LLM-generated payloads into test points
def generate_llm_payloads(requests, payloads_per_field=5):
    final_payloads = []

    for req in requests:
        method = req.get('method', 'GET').upper()
        url = req.get('url', '')
        body = req.get('body', '')

        if method == "GET" and '?' in url:
            base, query = url.split('?', 1)
            params = urllib.parse.parse_qs(query)

            for key in params:
                context = f"GET parameter: {key} in URL: {url}"
                llm_payloads = generate_xss_payloads_via_llm(context, num=payloads_per_field)

                for payload in llm_payloads:
                    injected_params = params.copy()
                    injected_params[key] = [payload]
                    new_query = urllib.parse.urlencode(injected_params, doseq=True)
                    final_payloads.append(f"{base}?{new_query}")

        elif method == "POST":
            params = urllib.parse.parse_qs(body)

            if not params and '=' in body:
                key = body.split('=')[0]
                context = f"POST body field: {key} in URL: {url}"
                llm_payloads = generate_xss_payloads_via_llm(context, num=payloads_per_field)

                for payload in llm_payloads:
                    new_body = urllib.parse.urlencode({key: payload})
                    final_payloads.append(f"POST to {url} | body: {new_body}")

            else:
                for key in params:
                    context = f"POST parameter: {key} in URL: {url}"
                    llm_payloads = generate_xss_payloads_via_llm(context, num=payloads_per_field)

                    for payload in llm_payloads:
                        injected_params = params.copy()
                        injected_params[key] = [payload]
                        new_body = urllib.parse.urlencode(injected_params, doseq=True)
                        final_payloads.append(f"POST to {url} | body: {new_body}")

    return list(set(final_payloads))  # Remove duplicates

# Save to file
def save_payloads_to_file(payloads, filename):
    with open(filename, 'w', encoding='utf-8') as f:
        for payload in payloads:
            f.write(payload + '\n')

# Main
if __name__ == "__main__":
    reqs = load_requests("request.json")
    payloads = generate_llm_payloads(reqs, payloads_per_field=5)
    save_payloads_to_file(payloads, "payloads.txt")
    print(f"[+] Generated {len(payloads)} payloads using LLM and saved to payloads.txt")
