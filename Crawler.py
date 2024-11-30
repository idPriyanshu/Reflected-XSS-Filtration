import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import json
import re

def sanitize_filename(url):
    # Remove invalid characters from the filename
    return re.sub(r'[<>:"/\\|?*\']', '_', url)

def save_html(url, content):
    # Create a folder for saving HTML files if it doesn't exist
    if not os.path.exists('html_files'):
        os.makedirs('html_files')

    # Generate a safe filename based on the URL
    safe_filename = sanitize_filename(url.replace('https://', '').replace('http://', '').replace('/', '_')) + '.html'
    file_path = os.path.join('html_files', safe_filename)

    # Save the HTML content to a file
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(content)
    print(f"Saved HTML content for: {url}")

def clear_files():
    # Clear url.txt
    with open('url.txt', 'w') as text_file:
        text_file.write("")  # Overwrite the file with empty content

    # Clear url_data.json
    with open('url_data.json', 'w') as json_file:
        json.dump([], json_file, indent=4)  # Write an empty JSON array

def clear_html_files():
    # Remove all HTML files in the html_files directory
    html_files_dir = 'html_files'
    if os.path.exists(html_files_dir):
        for file_name in os.listdir(html_files_dir):
            file_path = os.path.join(html_files_dir, file_name)
            if os.path.isfile(file_path):
                os.remove(file_path)
                

def crawl(url, visited, base_domain):
    if url in visited:  # Avoid re-crawling the same URL
        return
    visited.add(url)  # Mark the URL as visited

    urls_data = []  # List to collect formatted URLs

    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Save the HTML content of the main page
        save_html(url, response.text)

        # Extract all GET request links
        for link in soup.find_all('a', href=True):
            href = link['href']
            full_url = urljoin(url, href)  # Handles relative links

            # Only process URLs within the base domain
            if urlparse(full_url).netloc == base_domain:
                if full_url not in visited:  # Avoid adding already visited URLs
                    urls_data.append({"method": "GET", "url": full_url})
                    print(f"Found GET link: {full_url}")

                    # Recursively crawl internal links only
                    crawl(full_url, visited, base_domain)

        # Extract all POST request forms
        for form in soup.find_all('form'):
            form_action = form.get('action')
            form_method = form.get('method', 'GET').upper()
            if form_action and form_method == 'POST':
                full_url = urljoin(url, form_action)  # Handle relative form action

                # Only process forms within the base domain
                if urlparse(full_url).netloc == base_domain:
                    if full_url not in visited:  # Avoid adding already visited URLs
                        urls_data.append({"method": "POST", "url": full_url})
                        print(f"Found POST form: {full_url}")

                        # Save HTML of POST forms
                        form_response = requests.get(full_url)  # Fetching the form page
                        save_html(full_url, form_response.text)

        # Write all collected URLs to url.txt in the specified format (e.g., "METHOD URL")
        with open('url.txt', 'a') as text_file:  # Use 'a' to append to the file
            for entry in urls_data:
                formatted_entry = f"{entry['method']} {entry['url']}\n"
                text_file.write(formatted_entry)  # Write formatted entry to the file

        # Append URLs to url_data.json
        try:
            with open('url_data.json', 'r') as json_file:
                existing_data = json.load(json_file)
        except (FileNotFoundError, json.JSONDecodeError):
            existing_data = []

        existing_data.extend(urls_data)

        with open('url_data.json', 'w') as json_file:
            json.dump(existing_data, json_file, indent=4)

    except Exception as e:
        print(f"Failed to process {url}: {str(e)}")

# Start crawling the domain
u = input("Enter Domain for Crawling: ")
base_domain = urlparse(u).netloc  # Extract the base domain
visited_urls = set()  # Set to track visited URLs

# Clear previously stored data before starting the new crawl
clear_files()
clear_html_files()

crawl(u, visited_urls, base_domain)
