# llm-food-kcal-calculator

## Scraper Description

The `scraper_calories_info.py` script is a web scraper designed to collect nutritional information from calories.info. Here's how it works:

- Starts from the base URL (https://www.calories.info/)
- Recursively crawls through all linked pages on the website
- Saves each visited page as an HTML file in the `calories_info` directory
- Implements a visited set to prevent duplicate scraping
- Uses BeautifulSoup for HTML parsing and link extraction

### Usage

To run the scraper:

```bash
python scraper_calories_info.py
```

The script will create a `calories_info` directory and save all scraped pages there.
