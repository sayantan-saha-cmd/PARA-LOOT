import requests
import random
import time
import logging
import sys
import argparse
import os
from urllib.parse import urlparse, urljoin, parse_qs, urlencode
from bs4 import BeautifulSoup

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger()

# Spoofed headers for basic WAF evasion
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:54.0) Gecko/20100101 Firefox/54.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:54.0) Gecko/20100101 Firefox/54.0",
]

HARDCODED_EXTENSIONS = [
    ".jpg", ".jpeg", ".png", ".gif", ".pdf", ".svg", ".json",
    ".css", ".js", ".webp", ".woff", ".woff2", ".eot", ".ttf", ".otf", ".mp4", ".txt"
]

DELAY_MIN = 1
DELAY_MAX = 3
MAX_RETRIES = 3

def load_user_agent():
    return random.choice(USER_AGENTS)

def fetch_url_content(url, proxy=None):
    headers = {"User-Agent": load_user_agent()}
    proxies = {'http': proxy, 'https': proxy} if proxy else None
    for attempt in range(MAX_RETRIES):
        try:
            response = requests.get(url, headers=headers, proxies=proxies, timeout=10)
            response.raise_for_status()
            return response
        except requests.RequestException as e:
            logger.warning(f"Error fetching URL {url}: {e}. Retrying ({attempt+1}/{MAX_RETRIES})...")
            time.sleep(5)
        except KeyboardInterrupt:
            logger.warning("Keyboard Interrupt received. Exiting...")
            sys.exit()
    logger.error(f"Failed to fetch URL {url} after {MAX_RETRIES} retries.")
    sys.exit()

def has_extension(url, extensions):
    parsed_url = urlparse(url)
    path = parsed_url.path
    ext = os.path.splitext(path)[1].lower()
    return ext in extensions

def clean_url(url):
    parsed = urlparse(url)
    netloc = parsed.netloc
    if (parsed.port == 80 and parsed.scheme == "http") or (parsed.port == 443 and parsed.scheme == "https"):
        netloc = netloc.rsplit(":", 1)[0]
    cleaned = parsed._replace(netloc=netloc)
    return cleaned.geturl()

def clean_urls(urls, extensions, placeholder):
    cleaned_urls = set()
    for url in urls:
        cleaned_url = clean_url(url)
        if not has_extension(cleaned_url, extensions):
            parsed = urlparse(cleaned_url)
            query_params = parse_qs(parsed.query)
            cleaned_params = {k: placeholder for k in query_params}
            cleaned_query = urlencode(cleaned_params, doseq=True)
            cleaned_url = parsed._replace(query=cleaned_query).geturl()
            cleaned_urls.add(cleaned_url)
    return list(cleaned_urls)

def fetch_wayback_urls(domain, proxy=None):
    logger.info(f"[INFO] Fetching URLs for {domain} from Wayback Machine")
    wayback_url = f"https://web.archive.org/cdx/search/cdx?url={domain}/*&output=txt&collapse=urlkey&fl=original"
    response = fetch_url_content(wayback_url, proxy)
    urls = response.text.splitlines()
    logger.info(f"[INFO] Found {len(urls)} URLs from Wayback Machine")
    return urls

def extract_params_from_url(url):
    parsed = urlparse(url)
    params = parse_qs(parsed.query)
    return set(params.keys())

def crawl(domain, output_file_handle, proxy=None):
    if not domain.startswith("http"):
        domain = "http://" + domain
    base_domain = urlparse(domain).netloc

    to_crawl = [domain]
    visited = set()
    found_params = set()

    while to_crawl:
        url = to_crawl.pop(0)
        if url in visited:
            continue
        try:
            headers = {"User-Agent": load_user_agent()}
            proxies = {'http': proxy, 'https': proxy} if proxy else None
            response = requests.get(url, headers=headers, proxies=proxies, timeout=10)
            if response.status_code != 200:
                visited.add(url)
                continue
            content_type = response.headers.get("Content-Type", "")
            if "text/html" not in content_type:
                visited.add(url)
                continue

            output_file_handle.write(f"Crawling: {url}\n")
            output_file_handle.flush()

            soup = BeautifulSoup(response.text, "html.parser")

            params = extract_params_from_url(url)
            new_params = params - found_params
            for p in new_params:
                output_file_handle.write(f"Found parameter: {p}\n")
            found_params.update(params)
            links = set()
            for a_tag in soup.find_all("a", href=True):
                link = a_tag['href']
                full_link = urljoin(url, link)
                if urlparse(full_link).netloc == base_domain:
                    links.add(full_link)

            for link in links:
                params = extract_params_from_url(link)
                new_params = params - found_params
                for p in new_params:
                    output_file_handle.write(f"Found parameter: {p}\n")
                found_params.update(params)
                if link not in visited and link not in to_crawl:
                    to_crawl.append(link)

            visited.add(url)
            time.sleep(random.uniform(DELAY_MIN, DELAY_MAX))
        except Exception as e:
            output_file_handle.write(f"Request failed for {url}: {e}\n")
            output_file_handle.flush()
            visited.add(url)
            continue

    return found_params, visited

def main():
    logo = r"""
 ____   _    ____      _         _     ___   ___ _____ 
|  _ \ / \  |  _ \    / \       | |   / _ \ / _ \_   _|
| |_) / _ \ | |_) |  / _ \ _____| |  | | | | | | || |  
|  __/ ___ \|  _ <  / ___ \_____| |__| |_| | |_| || |  
|_| /_/   \_\_| \_\/_/   \_\    |_____\___/ \___/ |_|  
                                                       
❖━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━❖
✦  Created By       : Sayantan Saha                               ✦
✦  LinkedIn Profile : https://www.linkedin.com/in/mastersayantan/ ✦
✦  GitHub Profile   : https://github.com/sayantan-saha-cmd/       ✦
❖━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━❖
"""
    print(logo)

    parser = argparse.ArgumentParser(description="Combined ParamFinder with ParamSpider features")
    parser.add_argument("-d", "--domain", help="Target domain (e.g., example.com)")
    parser.add_argument("-l", "--output", help="Output filename to save results")
    parser.add_argument("--proxy", help="Proxy address (optional)", default=None)
    parser.add_argument("-p", "--placeholder", help="Placeholder for parameter values", default="FUZZ")

    args = parser.parse_args()

    if not args.domain:
        domain = input("Domain Name: ").strip()
    else:
        domain = args.domain

    if not args.output:
        output_file = input("File Name: ").strip()
    else:
        output_file = args.output

    proxy = args.proxy
    placeholder = args.placeholder

    logger.info(f"Fetching URLs from Wayback Machine for domain: {domain}")
    wayback_urls = fetch_wayback_urls(domain, proxy)
    cleaned_urls = clean_urls(wayback_urls, HARDCODED_EXTENSIONS, placeholder)

    logger.info(f"Found {len(cleaned_urls)} cleaned URLs with parameters")

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(f"Starting combined parameter discovery for domain: {domain}\n\n")

        # Write cleaned URLs with parameters
        f.write("Cleaned URLs from Wayback Machine:\n")
        total_urls = len(cleaned_urls)
        f.write(f"Total cleaned URLs: {total_urls}\n")
        count = 0
        for url in cleaned_urls:
            # Write all cleaned URLs regardless of '?'
            f.write(url + "\n")
            if "?" in url:
                count += 1
        f.write(f"\nTotal cleaned URLs with parameters (contain '?'): {count}\n\n")

        # Crawl domain to find additional parameters
        logger.info("Starting crawling to find additional parameters...")
        found_params, visited_urls = crawl(domain, f, proxy)

        # Generate fuzzed URLs
        base_url = domain if domain.startswith("http") else "http://" + domain
        f.write("\nFuzzed URLs:\n")
        for param in found_params:
            fuzzed_url = f"{base_url}/?{param}={placeholder}"
            f.write(fuzzed_url + "\n")

        f.write("\nParameter discovery complete.\n")

    logger.info(f"Results saved to {output_file}")

if __name__ == "__main__":
    main()
