import requests
from bs4 import BeautifulSoup

from senscritique.parse_utils import get_review_id
from senscritique.utils import get_base_url, read_soup_result


def get_critiques_url(user_name, page_no=1):
    url = get_base_url(user_name=user_name) + "critiques/page-" + str(page_no)

    return url


def parse_critiques_page(user_name="wok", page_no=1, verbose=False):
    url = get_critiques_url(user_name=user_name, page_no=page_no)
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

    collection_items = soup.find_all("article", {"class": "ere-review ere-box"})

    review_data = {}
    for item in collection_items:
        overview = item.find_all("button", {"class": "ere-review-overview"})
        title = item.find_all("h3", {"class": "d-heading2 ere-review-heading"})
        excerpt = item.find_all("p", {"class": "ere-review-excerpt"})
        game_system = item.find_all("span", {"class": "ere-review-gamesystem"})
        rating = item.find_all("div", {"class": "elrua-useraction-action"})
        link = item.find_all("a", {"class": "ere-review-anchor"})
        footer = item.find_all("footer", {"class": "ere-review-details"})

        item_id = get_review_id(overview)

        review_data[item_id] = {}
        review_data[item_id]["title"] = read_soup_result(title)
        review_data[item_id]["excerpt"] = read_soup_result(excerpt)
        review_data[item_id]["game_system"] = read_soup_result(game_system)
        review_data[item_id]["rating"] = read_soup_result(rating)
        review_data[item_id]["link"] = link[0].attrs["href"]
        review_data[item_id]["date"] = footer[0].find_all("time")[0].text

        full_review_url = get_base_url() + review_data[item_id]["link"]

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

        response = requests.get(full_review_url, headers=headers)
        full_soup = BeautifulSoup(response.content, "lxml")

        cover = full_soup.find_all("h1", {"class": "rvi-cover-title"})
        review_data[item_id]["full_title"] = read_soup_result(cover)

        review_items = full_soup.find_all("div", {"class": "d-grid-main"})

        print(review_data[item_id]["title"])

        for review_item in review_items:
            content = review_item.find_all("div", {"class": "rvi-review-content"})
            stats = review_item.find_all("div", {"data-rel": "likebar"})

            review_data[item_id]["content"] = read_soup_result(content)
            review_data[item_id]["upvotes"] = stats[0].attrs["data-sc-positive-count"]
            review_data[item_id]["downvotes"] = stats[0].attrs["data-sc-negative-count"]

            if verbose:
                print(
                    "-   item n°{}: (upvotes, downvotes) = ({}, {})".format(
                        item_id,
                        review_data[item_id]["upvotes"],
                        review_data[item_id]["downvotes"],
                    ),
                )

    return review_data
