import os
import json
import re
import time
import logging
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

# Setup logging
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "text/html,application/xhtml+xml"
}

def sanitize_filename(url):
    """Sanitize filename for saving HTML."""
    return re.sub(r'[<>:"/\\|?*\']', '_', url)

def save_html(url, content):
    """Save raw HTML content to file."""
    os.makedirs('html_files', exist_ok=True)
    safe_filename = sanitize_filename(urlparse(url).netloc + urlparse(url).path).strip('_') + '.html'
    file_path = os.path.join('html_files', safe_filename)
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        logging.info(f"[Saved HTML] {file_path}")
    except Exception as e:
        logging.warning(f"[Failed to Save HTML] {url}: {e}")

def clear_files():
    """Clear previous output files."""
    open('url.txt', 'w').close()
    with open('url_data.json', 'w') as jf:
        json.dump([], jf, indent=4)

def clear_html_files():
    """Delete all saved HTML files from previous run."""
    html_dir = 'html_files'
    if os.path.exists(html_dir):
        for filename in os.listdir(html_dir):
            filepath = os.path.join(html_dir, filename)
            if os.path.isfile(filepath):
                os.remove(filepath)

def is_html_page(url):
    """Check if URL points to a likely HTML resource."""
    return not re.search(r'\.(jpg|jpeg|png|gif|pdf|doc|zip|exe|svg|ico|css|js)(\?|$)', url, re.IGNORECASE)

def crawl(url, visited, base_domain):
    """Main crawling function."""
    if url in visited or not is_html_page(url):
        return
    visited.add(url)

    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        content_type = response.headers.get('Content-Type', '')
        if 'text/html' not in content_type:
            logging.warning(f"[Non-HTML Skipped] {url}")
            return

        soup = BeautifulSoup(response.text, 'html.parser')
        save_html(url, response.text)

        new_entries = []

        # Crawl GET links
        for tag in soup.find_all('a', href=True):
            href = urljoin(url, tag['href'])
            parsed = urlparse(href)
            if parsed.netloc == base_domain and is_html_page(href) and href not in visited:
                new_entries.append({"method": "GET", "url": href})
                logging.info(f"[Found GET] {href}")
                crawl(href, visited, base_domain)  # Recursive call

        # Crawl POST forms
        for form in soup.find_all('form'):
            form_method = form.get('method', 'GET').upper()
            form_action = form.get('action', '')
            action_url = urljoin(url, form_action)
            parsed = urlparse(action_url)
            if form_method == 'POST' and parsed.netloc == base_domain:
                entry = {"method": "POST", "url": action_url}
                if entry not in new_entries:
                    new_entries.append(entry)
                    logging.info(f"[Found POST] {action_url}")
                    try:
                        form_resp = requests.get(action_url, headers=HEADERS, timeout=10)
                        save_html(action_url, form_resp.text)
                    except:
                        logging.warning(f"[POST Fetch Failed] {action_url}")

        # Write to url.txt
        with open('url.txt', 'a') as txt_file:
            for entry in new_entries:
                txt_file.write(f"{entry['method']} {entry['url']}\n")

        # Write to url_data.json
        try:
            with open('url_data.json', 'r') as jf:
                data = json.load(jf)
        except (FileNotFoundError, json.JSONDecodeError):
            data = []

        # Avoid duplication in JSON
        for entry in new_entries:
            if entry not in data:
                data.append(entry)

        with open('url_data.json', 'w') as jf:
            json.dump(data, jf, indent=4)

        time.sleep(1)  # Rate limiting

    except Exception as e:
        logging.error(f"[Crawl Failed] {url}: {e}")

if __name__ == "__main__":
    user_input = input("Enter domain to crawl (e.g., https://example.com): ").strip()
    if not user_input.startswith("http"):
        user_input = "https://" + user_input

    base_domain = urlparse(user_input).netloc
    visited = set()

    clear_files()
    clear_html_files()

    logging.info(f"[Starting Crawl] Base domain: {base_domain}")
    crawl(user_input, visited, base_domain)
    logging.info("[Crawling Complete]")
