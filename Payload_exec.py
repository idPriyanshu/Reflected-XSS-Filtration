import requests
import json

# Function to read XSS payloads from a file
def read_payloads_from_file(filename):
    with open(filename, 'r') as file:
        return [line.strip() for line in file.readlines()]

# Function to parse requests from a JSON file
def parse_requests_from_file(filename):
    with open(filename, 'r') as file:
        return json.load(file)  # Load JSON data

# Function to inject XSS payloads into URLs or request bodies
def inject_xss_payloads(req, payloads):
    modified_requests = []

    if req['method'] == 'GET':
        for payload in payloads:
            # Inject payload as a query parameter
            modified_url = f"{req['url']}?{req.get('body', '')}xss_test={payload}"
            modified_requests.append({
                "url": modified_url,
                "injection_point": f"GET URL: {modified_url}"  # Specify the complete URL with payload
            })

    elif req['method'] == 'POST':
        for payload in payloads:
            # Inject payload into the body
            body = f"{req.get('body', '')}xss_test={payload}"
            modified_requests.append({
                "url": req['url'],
                "body": body,
                "injection_point": f"POST Body: {body}"  # Specify the complete body with payload
            })

    return modified_requests

# Function to send XSS test requests
def send_xss_test_requests(requests_list, payloads, output_file):
    with open(output_file, "w") as result_file:
        for req in requests_list:
            print(f"Request structure: {req}")  # Debugging line to check request structure

            # Ensure headers are a dictionary
            headers = req.get('headers', {})
            print(f"Headers before request: {headers}, Type: {type(headers)}")  # Debug the headers

            if not isinstance(headers, dict):
                print(f"Error: Headers is not a dictionary. Found: {type(headers)}")
                continue  # Skip this iteration if headers are not a dictionary

            if req['method'] == 'GET':
                modified_requests = inject_xss_payloads(req, payloads)
                for modified_req in modified_requests:
                    try:
                        print(f"Sending GET request to: {modified_req['url']} with headers: {headers}")
                        response = requests.get(modified_req['url'], headers=headers)
                        result_file.write(f"GET {modified_req['url']} - Status: {response.status_code}\n")
                        result_file.write(f"Injection Point: {modified_req['injection_point']}\n")  # Include injection point
                        result_file.write(f"Response Headers: {response.headers}\n")
                        result_file.write(f"Response Body: {response.text[:500]}...\n\n")
                    except Exception as e:
                        print(f"Failed to GET {modified_req['url']}: {str(e)}\n")
                        result_file.write(f"GET {modified_req['url']} - Error: {str(e)}\n\n")

            elif req['method'] == 'POST':
                if 'body' in req:
                    modified_requests = inject_xss_payloads(req, payloads)
                    for modified_req in modified_requests:
                        headers['Content-Length'] = str(len(modified_req['body']))  # Update Content-Length
                        try:
                            print(f"Sending POST request to: {modified_req['url']} with body: {modified_req['body']} and headers: {headers}")
                            response = requests.post(modified_req['url'], headers=headers, data=modified_req['body'])
                            result_file.write(f"POST {modified_req['url']} with payload: {modified_req['body']} - Status: {response.status_code}\n")
                            result_file.write(f"Injection Point: {modified_req['injection_point']}\n")  # Include injection point
                            result_file.write(f"Response Headers: {response.headers}\n")
                            result_file.write(f"Response Body: {response.text[:500]}...\n\n")
                        except Exception as e:
                            print(f"Failed to POST {modified_req['url']} with payload {modified_req['body']}: {str(e)}\n")
                            result_file.write(f"POST {modified_req['url']} with payload {modified_req['body']} - Error: {str(e)}\n\n")

# Main function
if __name__ == "__main__":
    requests_list = parse_requests_from_file("request.json")  # Changed to read from JSON
    xss_payloads = read_payloads_from_file("payloads.txt")
    output_file = "results.txt"
    send_xss_test_requests(requests_list, xss_payloads, output_file)
