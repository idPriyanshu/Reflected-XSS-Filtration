import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import json

def create_request_file(url_list):
    # Clear the content of request.json before writing new data
    requests_data = []  # To collect requests

    # Process each URL in the list
    for entry in url_list:
        method = entry['method']
        url = entry['url']
        
        if method == 'GET':
            request_data = process_get_request(url)  # Get URL for GET request
            if request_data:
                requests_data.append(request_data)
        elif method == 'POST':
            request_data = process_post_request(url)  # Get URL for POST request
            if request_data:
                requests_data.extend(request_data)  # Extend with multiple POST requests

    # Write all requests to request.json
    with open('request.json', 'w') as req_file:
        json.dump(requests_data, req_file, indent=4)  # Save as pretty-printed JSON

def process_get_request(url):
    try:
        parsed_url = urlparse(url)
        host = parsed_url.netloc  # Extract the host using urlparse

        # Create GET request details
        request_details = {
            "method": "GET",
            "url": url,
            "headers": {
                "Host": host,
                "User-Agent": "Mozilla/5.0",  # Example header
                "Accept": "*/*"
            },
            "body": ""
        }
        print(f"Added GET request for: {url}")
        return request_details

    except Exception as e:
        print(f"Failed to process GET request for {url}: {str(e)}")
        return None

def process_post_request(url):
    requests_data = []  # To collect requests

    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        parsed_url = urlparse(url)
        host = parsed_url.netloc

        # Process all forms for POST requests
        for form in soup.find_all('form'):
            form_action = form.get('action')
            if not form_action.startswith('http'):
                form_action = url.rstrip('/') + '/' + form_action.lstrip('/')

            # Collect form inputs
            inputs = {}
            for input_tag in form.find_all(['input', 'textarea', 'select']):
                input_name = input_tag.get('name')
                input_value = input_tag.get('value', '')
                if input_name:
                    inputs[input_name] = input_value

            # Prepare POST body
            post_data = '&'.join([f"{k}={v}" for k, v in inputs.items()])

            # Create POST request details
            request_details = {
                "method": "POST",
                "url": form_action,
                "headers": {
                    "Host": host,
                    "Content-Type": "application/x-www-form-urlencoded",
                    "Content-Length": str(len(post_data)),
                    "User-Agent": "Mozilla/5.0",
                    "Accept": "*/*"
                },
                "body": post_data
            }
            requests_data.append(request_details)
            print(f"Added POST request for: {form_action}")

        return requests_data

    except Exception as e:
        print(f"Failed to process POST request for {url}: {str(e)}")
        return None

# Read URLs from url.txt
with open('url.txt', 'r') as url_file:
    urls = url_file.readlines()

# Start generating request.json
url_list = [{"method": line.split()[0], "url": line.split()[1]} for line in urls if line.strip()]  # Convert lines to a list of dicts
create_request_file(url_list)
