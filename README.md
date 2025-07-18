# 🛡️ Reflected XSS Filtration

An end-to-end, Python-based toolkit to **detect Reflected Cross-Site Scripting (XSS)** vulnerabilities in web applications. Combines **traditional payloads** with **LLM-generated adaptive payloads**, along with full crawling, injection, response logging, and vulnerability analysis.

---

## 🔍 Purpose

Modern applications are better at input filtering — so detecting XSS requires both brute testing and intelligent payload crafting. This tool automates that process:

- Crawls target pages and extracts potential input endpoints (GET/POST)
- Generates payloads using **LLM-enhanced** logic
- Sends payloads and captures responses
- Analyzes reflections to identify XSS vulnerabilities
- Logs structured results for review and triage

---

## 👤 Contributors

- [@maithilmishra](https://github.com/maithilmishra)
- [@Piyush3012](https://github.com/Piyush3012)

---

## 📁 Directory Overview

| File / Folder               | Purpose |
|----------------------------|---------|
| `crawler.py`               | Crawls the given URL, saves HTML & endpoint URLs |
| `endpoints methods.py`     | Extracts HTTP methods and request metadata |
| `injection.py`             | Injects payloads into discovered input points |
| `injection analysis.py`    | Analyzes responses for reflected payloads |
| `llm_payloads.py`          | Generates XSS payloads using LLM (e.g., GPT) |
| `payload generation.py`    | Combines LLM/traditional payloads into one list |
| `html_files/`              | HTML pages saved during crawl |
| `url.txt`                  | List of discovered URLs during crawl |
| `url_data.json`            | Structured metadata (URL, method, params) |
| `payloads.txt`             | Final payload list used for injection |
| `request.json`             | Metadata of requests to be sent |
| `results.txt`              | Raw responses from server after injection |
| `analysis_results.txt`     | Final vulnerability report |
| `requirements.txt`         | Python dependencies (see below) |

---

## 📦 Installation

```bash
git clone https://github.com/your-username/Reflected-XSS-Filtration.git
cd Reflected-XSS-Filtration
pip install -r requirements.txt
````

**`requirements.txt` includes:**

* `beautifulsoup4`
* `requests`
* `json`
* `re`
* `urllib3`
* `jsonschema`
* `pandas`
* LLM SDK (openrouter)

---

## ⚙️ Workflow

### 1️⃣ Crawl Target Site

```bash
python crawler.py
```

* Extracts all reachable pages
* Saves raw HTML in `/html_files`
* Outputs URLs in `url.txt`
* Metadata in `url_data.json`

---

### 2️⃣ Extract HTTP Methods

```bash
python "endpoints methods.py"
```

* Parses URLs
* Detects input forms / query params (GET/POST)
* Outputs method/param info into `request.json`

---

### 3️⃣ Generate Payloads (LLM-enhanced)

```bash
python "payload generation.py"
```

* Sends context (parameter name, endpoint) to an LLM API via *llm_payloads.py*
* Receives adaptive, filtered-bypass payloads
* Saves to `payloads.txt`

> ✅ LLM-generated payloads replace traditional static lists.
> 📍 You can tweak the prompt inside `llm_payloads.py` to adapt to bypass needs.

---

### 4️⃣ Inject Payloads

```bash
python injection.py
```

* Injects each payload into all identified input points
* Logs server responses into `results.txt`

---

### 5️⃣ Analyze Reflections

```bash
python "injection analysis.py"
```

* Detects reflected payloads
* Context-aware filtering (e.g., inside HTML, JS, attributes)
* Generates vulnerability report in `analysis_results.txt`

---

## 📄 Key Output Files Explained

| File                   | Description                                  |
| ---------------------- | -------------------------------------------- |
| `url.txt`              | List of discovered endpoints during crawl    |
| `url_data.json`        | List of URL + method + param structures      |
| `payloads.txt`         | LLM-crafted payloads for injection           |
| `results.txt`          | Response bodies after injection              |
| `analysis_results.txt` | Final detected reflected XSS cases           |
| `request.json`         | Request template data (URL, headers, params) |

---

## 🧪 Sample Finding

```
{
  "payload": "POST to https://xyz.com/<url endpoint> | body: p1=<payloaf>",
  "url": "https://xyz.com/<url endpoint>",
  "method": "POST",
  "status_code": 200,
  "reflected": True,
  "reflection_type": "script"
}
```

---

## 🤖 How LLM Helps

The `llm_payloads.py` module sends prompts like:

> “Generate 5 reflected XSS payloads for parameter `search` in a GET request. The server filters `<`, `script`, and quotes. Focus on JS event handlers.”

LLMs return:

* Obfuscated payloads
* Encoded versions
* Event-based triggers (`onerror`, `onmouseover`)
* JS tricks (`srcdoc`, `iframe`, etc.)

This is **especially effective** on lightly filtered or context-aware input forms.

---

## 🗺️ Roadmap / Enhancements

* [ ] 🌐 Web interface (Flask)
* [ ] 🧠 Payload auto-mutation via GPT + reinforcement
* [ ] 🔍 DOM-based XSS detection via headless browser
* [ ] 📊 Dashboard-style result visualization
* [ ] 🔐 CSP & WAF bypass logic

---

## ⚠️ Disclaimer

> This tool is for **educational and ethical testing** only.
> Do **not** test websites or systems without explicit permission.

---