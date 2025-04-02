# llm-food-kcal-calculator

## Scripts Description

### 1. Scraper (`scraper_calories_info.py`)

The `scraper_calories_info.py` script is a web scraper designed to collect nutritional information from calories.info. Here's how it works:

- Starts from the base URL (https://www.calories.info/)
- Recursively crawls through all linked pages on the website
- Saves each visited page as an HTML file in the `calories_info` directory
- Implements a visited set to prevent duplicate scraping
- Uses BeautifulSoup for HTML parsing and link extraction

### 2. HTML Cleaner (`clean_html_files.py`)

The `clean_html_files.py` script processes the scraped HTML files to extract only relevant nutritional information:

- Removes unnecessary HTML elements (ads, navigation, etc.)
- Keeps only divs with specific classes containing nutritional data
- Maintains the original directory structure
- Saves cleaned files to `calories_info_processed` directory
- Uses BeautifulSoup for HTML processing and cleaning

### 3. Document Ingestion (`ingestion.py`)

The `ingestion.py` script prepares the cleaned HTML files for use with LangChain:

- Recursively processes all HTML files from `calories_info_processed`
- Extracts text content from HTML files
- Splits content into chunks using LangChain's RecursiveCharacterTextSplitter
- Creates Document objects with metadata
- Prepares documents for vector storage (Pinecone)

## Usage

1. First, run the scraper to collect data:

```bash
python scraper_calories_info.py
```

2. Then, clean the HTML files:

```bash
python clean_html_files.py
```

3. Finally, ingest the cleaned documents:

```bash
python ingestion.py
```

Note: Make sure to set up your environment variables (like Pinecone API key) before running the ingestion script.
