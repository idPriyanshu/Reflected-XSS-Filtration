import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
import json
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')

def create_request_file(url_list):
    requests_data = []

    for entry in url_list:
        method = entry['method'].upper()
        url = entry['url'].strip()

        if not url.startswith('http'):
            logging.warning(f"Skipping invalid URL: {url}")
            continue

        if method == 'GET':
            request_data = process_get_request(url)
            if request_data:
                requests_data.append(request_data)

        elif method == 'POST':
            request_data = process_post_request(url)
            if request_data:
                requests_data.extend(request_data)

    with open('request.json', 'w') as req_file:
        json.dump(requests_data, req_file, indent=4)
    logging.info("All requests written to request.json")

def process_get_request(url):
    try:
        parsed_url = urlparse(url)
        host = parsed_url.netloc

        return {
            "method": "GET",
            "url": url,
            "headers": {
                "Host": host,
                "User-Agent": "Mozilla/5.0",
                "Accept": "*/*"
            },
            "body": ""
        }
    except Exception as e:
        logging.error(f"GET request failed for {url}: {e}")
        return None

def process_post_request(url):
    requests_data = []

    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        parsed_url = urlparse(url)
        host = parsed_url.netloc

        for form in soup.find_all('form'):
            form_action = form.get('action') or url
            form_url = urljoin(url, form_action)  # Safe join for relative URLs

            # Collect input fields
            inputs = {}
            for input_tag in form.find_all(['input', 'textarea', 'select']):
                name = input_tag.get('name')
                value = input_tag.get('value', '')
                if name:
                    inputs[name] = value

            post_data = '&'.join([f"{k}={v}" for k, v in inputs.items()])

            request_details = {
                "method": "POST",
                "url": form_url,
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
            logging.info(f"Added POST request for: {form_url}")

        return requests_data

    except Exception as e:
        logging.error(f"POST request failed for {url}: {e}")
        return None

if __name__ == "__main__":
    try:
        with open('url.txt', 'r') as url_file:
            urls = url_file.readlines()
        url_list = [
            {"method": line.split()[0], "url": line.split()[1]}
            for line in urls if line.strip()
        ]
        create_request_file(url_list)
    except Exception as e:
        logging.critical(f"Error loading URLs: {e}")
