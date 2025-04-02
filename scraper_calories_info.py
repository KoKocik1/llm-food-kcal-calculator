import requests
from bs4 import BeautifulSoup
import os
import time
from urllib.parse import urljoin

base_url = "https://www.calorieking.com/us/en/foods/"
visited = set()


def scrape_page(url):
    """
    Scrape the page and save it to the folder.
    """
    if url in visited:
        return
    visited.add(url)

    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return

    html = response.text
    page_name = url.replace(base_url, "") + ".html"

    full_path = os.path.join("calories_info", page_name)

    os.makedirs(os.path.dirname(full_path), exist_ok=True)

    with open(full_path, "w", encoding="utf-8") as file:
        file.write(html)

    soup = BeautifulSoup(html, "html.parser")
    for link in soup.find_all("a", href=True):
        next_url = link["href"]
        next_url = urljoin(base_url, next_url)
        if next_url.startswith(base_url) and next_url not in visited:
            scrape_page(next_url)


if __name__ == "__main__":
    scrape_page(base_url)
