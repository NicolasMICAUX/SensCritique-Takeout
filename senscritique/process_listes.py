import requests
from bs4 import BeautifulSoup, Tag

from senscritique.parse_utils import get_item_id, get_num_pages
from senscritique.utils import get_base_url, get_url_for_liste, read_soup_result


def get_listes_url(user_name, page_no=1):
    url = get_base_url(user_name=user_name) + "listes?page=" + str(page_no)
    return url


def parse_listes_page(user_name="wok", page_no=1, verbose=False):
    url = get_listes_url(user_name=user_name, page_no=page_no)
    print(url)

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

    collection_items = soup.find_all(attrs={"data-testid": "list-card"})

    listes_data = {}

    for item in collection_items:
        # Ensure item is a Tag
        if not isinstance(item, Tag):
            continue
        anchor_tag = item.find("a")
        if not isinstance(anchor_tag, Tag):
            continue
        link = anchor_tag.get("href")
        if not isinstance(link, str) or not link:
            continue

        # Extend the link with the base URL
        link = get_base_url() + link

        try:
            item_id = int(link.rsplit("/", 1)[-1])
        except ValueError:
            continue

        listes_data[item_id] = {}
        listes_data[item_id]["link"] = link

        num_pages = get_num_pages(link)

        listes_data[item_id]["elements"] = {}

        for page_no_within_list in range(1, num_pages + 1):
            current_url = f"{link}?page={page_no_within_list}"

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

            response = requests.get(current_url, headers=headers)
            full_soup = BeautifulSoup(response.content, "lxml")

            title = full_soup.find_all(attrs={"data-testid": "list-title"})
            description = full_soup.find_all("span", {"data-testid": "linkify-text"})
            listes_data[item_id]["title"] = read_soup_result(title)
            listes_data[item_id]["description"] = read_soup_result(description)

            review_items = full_soup.find_all(attrs={"data-testid": "product-list-item"})

            for review_item in review_items:
                soup_content = review_item.find_all(attrs={"data-testid": "product-title"})
                # soup_comment = review_item.find_all(
                #     "div",
                #     {"class": "elli-annotation-content"},
                # )

                element = get_item_id(soup_content)
                name = read_soup_result(soup_content)
                # comment = read_soup_result(soup_comment, simplify_text=False)

                listes_data[item_id]["elements"][element] = {}
                listes_data[item_id]["elements"][element]["name"] = name
                # listes_data[item_id]["elements"][element]["comment"] = comment

    return listes_data
