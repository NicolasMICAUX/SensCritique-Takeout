import re
from calendar import c

import requests
from bs4 import BeautifulSoup
from persist_cache.persist_cache import cache

from senscritique.parse_utils import get_item_id
from senscritique.utils import get_base_url, read_soup_result


def get_collection_url(user_name, page_no=1):
    url = get_base_url(user_name=user_name) + "collection?page=" + str(page_no)
    return url


@cache(expiry=24 * 60 * 60)  # 24 hours cache
def parse_collection_page(user_name="wok", page_no=1, verbose=False):
    url = get_collection_url(user_name=user_name, page_no=page_no)

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

    collection_items = soup.find_all(attrs={"data-testid": "product-list-item"})

    data = {}
    for item in collection_items:
        actions_info = item.find(attrs={"data-testid": "actions-info"})
        user_rating = (
            actions_info.find_all(attrs={"data-testid": "Rating"})
            if actions_info
            else []
        )

        item_type = "unknown"
        creators_cat = item.find(attrs={"data-testid": "creators-category"})
        if creators_cat:
            first_span = creators_cat.find("span", recursive=False)
            if first_span:
                txt = first_span.get_text(strip=True)
            else:
                txt = creators_cat.get_text(strip=True)
            if txt:
                item_type = txt.lower()

        name = item.find_all(attrs={"data-testid": "product-title"})
        release_date = None
        clean_title = ""
        if name:
            raw_text = name[0].get_text(strip=True)
            m = re.search(r"^(.*?)[ \t]*\((\d{4})\)\s*$", raw_text)
            if m:
                clean_title = m.group(1).strip()
                release_date = m.group(2)

        # game_system = item.find_all("span", {"class": "elco-gamesystem"})
        # release_date = item.find_all("span", {"class": "elco-date"})
        # description = item.find_all("p", {"class": "elco-baseline elco-options"})
        creators_el = item.find(attrs={"data-testid": "creators"})
        author = creators_el.find_all("a") if creators_el else []

        site_rating = item.find_all(class_=re.compile(r"\bglobalRating\b"))
        site_rating = read_soup_result(site_rating)

        item_id = get_item_id(name)

        user_rating = read_soup_result(user_rating)
        data[item_id] = {}
        data[item_id]["name"] = clean_title
        data[item_id]["author"] = read_soup_result(author)
        data[item_id]["user_rating"] = float(user_rating) if user_rating else None
        data[item_id]["site_rating"] = float(site_rating) if site_rating else None
        # data[item_id]["description"] = read_soup_result(description)
        # data[item_id]["game_system"] = read_soup_result(game_system)
        data[item_id]["release_date"] = int(release_date) if release_date else None
        data[item_id]["item_type"] = item_type

        if verbose:
            print(
                "-   item n°{}: {}".format(
                    item_id,
                    data[item_id]["name"],
                ),
            )

    return data
