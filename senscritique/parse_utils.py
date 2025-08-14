import requests
from bs4 import BeautifulSoup
from persist_cache.persist_cache import cache


def get_item_id(soup_name):
    href = soup_name[0].get("href", "")
    if href:
        return href.rstrip("/").split("/")[-1]
    return ""


def get_review_id(soup_name):
    return soup_name[0].attrs["data-sc-review-id"]


@cache(expiry=24 * 60 * 60)  # 24 hours cache
def get_num_pages(url):
    # Add headers to avoid Cloudflare blocking
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "fr-FR,fr;q=0.9,en;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "DNT": "1",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
    }

    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, "lxml")
    # Extract last pager element with data-testid="click" and parse its text to int
    pager_elems = soup.find_all(attrs={"data-testid": "click"})
    try:
        raw_text = pager_elems[-1].get_text(strip=True)
        digits = "".join(ch for ch in raw_text if ch.isdigit())
        num_pages = int(digits) if digits else 1
    except (IndexError, ValueError):
        num_pages = 1

    return num_pages
