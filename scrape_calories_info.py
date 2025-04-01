import requests
from bs4 import BeautifulSoup

base_url = "https://www.calories.info/"
visited = set()


def scrape_page(url):
    """
    Scrape the page and save it to the folder.
    """
    if url in visited:
        return
    visited.add(url)

    response = requests.get(url)
    if response.status_code == 200:
        html = response.text
        page_name = url.replace(base_url, "").replace("/", "_") + ".html"
        with open(f"calories_info/{page_name}", "w", encoding="utf-8") as file:
            file.write(html)

        soup = BeautifulSoup(html, "html.parser")
        for link in soup.find_all("a", href=True):
            next_url = link["href"]
            if next_url.startswith("/"):
                scrape_page(base_url + next_url)


if __name__ == "__main__":
    scrape_page(base_url)
