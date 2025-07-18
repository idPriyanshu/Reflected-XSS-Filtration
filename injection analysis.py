import json
import re
import urllib.parse
import ast

def load_json_objects(file_path):
    """Load multiple JSON objects from a single file (not a JSON array)."""
    with open(file_path, 'r', encoding='utf-8') as f:
        data = f.read()

    # Find all top-level JSON objects using regex
    raw_objects = re.findall(r'\{.*?\}(?=\s*\{|\s*$)', data, re.DOTALL)
    parsed_objects = []

    for obj in raw_objects:
        try:
            parsed = json.loads(obj)
            parsed_objects.append(parsed)
        except json.JSONDecodeError:
            continue  # Skip invalid JSON parts

    return parsed_objects

def decode_payload(payload_string):
    """Extract and decode the actual payload from the POST string."""
    try:
        match = re.search(r'body:\s*([^|]+)', payload_string)
        if match:
            body = match.group(1).strip()
            decoded = urllib.parse.unquote_plus(body)  # decode URL encoding

            # Extract payload value from string like: p1={'payload': '<script>...</script>'}
            payload_match = re.search(r"p1=({.*})", decoded)
            if payload_match:
                payload_dict_str = payload_match.group(1)
                payload_dict = ast.literal_eval(payload_dict_str)  # safe eval to dict
                return payload_dict.get("payload", "(Missing 'payload' key)")
            
            return decoded  # fallback
    except Exception as e:
        return f"(Could not decode payload: {e})"

def analyze_payloads(results, save_to="analysis_results.txt"):
    total = len(results)
    reflected = [r for r in results if r.get('reflected') is True]
    not_reflected = [r for r in results if not r.get('reflected')]

    summary_lines = [
        "\n🔎 XSS Payload Analysis Summary:",
        "--------------------------------",
        f"Total Payloads Tested : {total}",
        f"Payloads Reflected    : {len(reflected)}",
        f"Payloads Not Reflected: {len(not_reflected)}",
        "",
        "Reflected Payloads:\n"
        "-------------------------\n"
    ]

    for r in reflected:
        payload_url = r.get("payload", "")
        decoded_payload = decode_payload(payload_url)
        summary_lines.append(f"-  Payload URL: {payload_url}")
        summary_lines.append(f"   Payload: {decoded_payload}")
        summary_lines.append(f"   Reflection Type: {r.get('reflection_type', 'N/A')}")
        summary_lines.append(f"   URL: {r.get('url')}\n")

    summary_lines.append("")
    summary_lines.append("Not Reflected Payloads:")
    summary_lines.append("-------------------------")
    for r in not_reflected:
        payload_url = r.get("payload", "")
        decoded_payload = decode_payload(payload_url)
        summary_lines.append(f"-  Payload URL: {payload_url}")
        summary_lines.append(f"   Payload: {decoded_payload}")
        summary_lines.append(f"   URL: {r.get('url')}\n")

    # Save to file
    with open(save_to, 'w', encoding='utf-8') as out:
        out.write("\n".join(summary_lines))

    print(f"\n✅ Saved full analysis to: {save_to}")

if __name__ == "__main__":
    file_path = "results.txt"
    results = load_json_objects(file_path)
    
    if not results:
        print("⚠️ No valid JSON objects found. Please check the format of results.txt.")
    else:
        analyze_payloads(results)
