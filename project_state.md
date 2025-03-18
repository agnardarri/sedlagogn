# Icelandic Central Bank Data Scraper

## Project Overview
A Python-based web scraping system for extracting, organizing, and downloading data from the Central Bank of Iceland (Seðlabanki Íslands) website. The project follows a multi-stage approach to catalog and retrieve financial datasets.

## Project Components

### 1. Page Links Scraper (`scrape_links_v2.py`)
**Status:** ✅ Complete

**Purpose:** Scrapes the main categories and subcategories from the Central Bank website.

**Features:**
- Creates hierarchical structure of categories and subcategories
- Extracts and parses date information (`last_update` and `next_update`)
- Intelligently detects update frequency

**Output:** `backend/scraper/page_links.yaml`

### 2. Data Links Scraper (`scrape_data_links.py`)
**Status:** ✅ Complete

**Purpose:** For each subcategory page, scrapes the available data links.

**Features:**
- Locates the "Tímaraðir" section containing data links
- Handles both relative and absolute URLs
- Implements smart staleness detection based on update dates
- Organizes output in a hierarchical structure with controlled field order

**Output:** `backend/scraper/data_links.yaml`

### 3. Data Downloader (`download_data.py`)
**Status:** ✅ Complete

**Purpose:** Downloads files from data links for specific subcategories.

**Features:**
- Searches for subcategory by name across all categories
- Downloads all data files associated with matching subcategories
- Saves files to a flat cache directory
- Handles filename conflicts with unique naming
- Provides download statistics and error reporting

**Output:** Data files in `backend/cache/`

## Technical Specifications

### Key Constants
- Base URL: `ROOT = "https://www.sedlabanki.is"`

### Directory Structure
- `backend/scraper/` - Contains all scraper scripts
- `backend/cache/` - Storage for downloaded data files
- `backend/scraper/page_links.yaml` - Category and subcategory mapping
- `backend/scraper/data_links.yaml` - Data links for each subcategory

### Dependencies
- requests - HTTP requests
- BeautifulSoup - HTML parsing
- yaml - Data storage format
- urllib3 - URL handling utilities
- datetime - For date manipulation and staleness detection

## Current Status
The core scraping infrastructure is complete and operational. The system can:
1. Catalog all categories and subcategories from the main site
2. Extract data links from each subcategory page
3. Download data files for specific subcategories based on name

## Next Steps and Potential Improvements

### Short-term
- Add more robust error handling and retry logic
- Implement proper logging instead of print statements
- Add rate limiting to be respectful to the server

### Mid-term
- Create a unified CLI interface for all scraping operations
- Add asynchronous processing for improved download performance
- Implement more comprehensive data validation

### Long-term
- Build data processing pipeline for the downloaded files
- Create visualization components for the extracted data
- Implement scheduled scraping to keep data updated automatically

## Usage Examples

### Scrape All Categories and Subcategories
```python
python backend/scraper/scrape_links_v2.py
```

### Scrape Data Links from Subcategory Pages
```python
python backend/scraper/scrape_data_links.py
```

### Download Files for a Specific Subcategory
```python
python backend/scraper/download_data.py "Tryggingafélög"
```

## Known Issues and Limitations
- No built-in rate limiting
- Limited validation of downloaded file content
- No automated workflow for end-to-end operation 