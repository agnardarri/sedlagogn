import os
import yaml
import requests
import subprocess
from datetime import datetime
from bs4 import BeautifulSoup
import urllib3

# Suppress InsecureRequestWarning
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def load_page_links(yaml_path='backend/scraper/page_links.yaml'):
    """Load the page links data from YAML file"""
    if not os.path.exists(yaml_path):
        print(f"Warning: {yaml_path} not found, running page links scraper first")
        subprocess.run(['python', 'backend/scraper/scrape_links_v2.py'])
        
    with open(yaml_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def is_url_stale(subcategory):
    """Check if a URL needs to be refreshed based on next_update date"""
    # Skip check if missing dates
    if not subcategory.get('next_update'):
        return False
        
    # Parse the next update date
    next_update = datetime.strptime(subcategory['next_update'], '%Y-%m-%d').date()
    today = datetime.now().date()
    
    # If next_update date has passed, the URL is stale
    return today >= next_update

def refresh_subcategory_url(category_name, subcategory_name):
    """Re-scrape the main page for an updated URL for this specific subcategory"""
    print(f"Refreshing URL for {category_name} > {subcategory_name}...")
    
    # Run the page links scraper to get fresh data
    subprocess.run(['python', 'backend/scraper/scrape_links_v2.py'])
    
    # Load the updated data
    links_data = load_page_links()
    
    # Find the specific subcategory
    for category in links_data:
        if category['category'] == category_name:
            for subcat in category['subcategories']:
                if subcat['name'] == subcategory_name:
                    return subcat
    
    return None

def scrape_data_links_from_page(url):
    """
    Scrape data links from a page by:
    1. Locating the one h2 element with text "Tímaraðir"
    2. Finding anchor elements in div next to the h2
    """
    print(f"  Scraping data links from {url}")
    
    try:
        # Get the page content
        ROOT = "https://www.sedlabanki.is"
        response = requests.get(ROOT + url, verify=False, timeout=30)
        response.raise_for_status()
        
        # Parse the HTML
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find h2 element containing "Tímaraðir" using the string parameter
        target_h2 = soup.find('h2', string=lambda text: "Tímaraðir" in text if text else False)
        # Find all anchor elements that come after the h2 element
        els = target_h2.find_next('div').find_all('a')
        return [{'name': el.get_text(), 'url': el['href']} for el in els]
        
    except Exception as e:
        print(f"  Error scraping {url}: {str(e)}")
        return []

def main():
    # Load page links data
    links_data = load_page_links()
    
    # Set up hierarchical result structure
    result = []
    
    # Process each category
    for category in links_data:
        category_name = category['category']
        
        # Create category entry
        category_entry = {
            'category': category_name,
            'subcategories': []
        }
        
        # Process each subcategory
        for subcategory in category['subcategories']:
            subcategory_name = subcategory['name']
            current_url = subcategory['url']
            
            # Check if URL is stale and needs refresh
            if is_url_stale(subcategory):
                print(f"URL is stale for {subcategory_name} - last updated: {subcategory.get('last_update')}, next update: {subcategory.get('next_update')}")
                
                # Get refreshed subcategory data
                updated_subcategory = refresh_subcategory_url(category_name, subcategory_name)
                
                if updated_subcategory:
                    # Use the refreshed URL and dates
                    subcategory = updated_subcategory
                    current_url = subcategory['url']
                    print(f"Updated URL: {current_url}")
                    print(f"New last_update: {subcategory.get('last_update')}")
                    print(f"New next_update: {subcategory.get('next_update')}")
            
            # Now process the URL (stale or fresh)
            try:
                print(f"Processing {subcategory_name} from {current_url}")
                
                # Scrape data links from the page
                data_links = scrape_data_links_from_page(current_url)
                
                # Skip if no data links
                if not data_links:
                    print(f"  No data links found for {subcategory_name}")
                    continue
                
                # Create subcategory entry
                subcategory_entry = {
                    'name': subcategory_name,
                    'links': data_links
                }
                
                # Add to category's subcategories list
                category_entry['subcategories'].append(subcategory_entry)
                
            except Exception as e:
                print(f"Error processing {subcategory_name}: {str(e)}")
        
        # Only add categories that have subcategories with links
        if category_entry['subcategories']:
            result.append(category_entry)
    
    # Define a custom YAML representer to force field order
    def represent_dict_order(self, data):
        if 'category' in data and 'subcategories' in data:
            # Order for category entries: category, then subcategories
            return self.represent_mapping('tag:yaml.org,2002:map', [
                ('category', data['category']), 
                ('subcategories', data['subcategories'])
            ])
        elif 'name' in data and 'links' in data:
            # Order for subcategory entries: name, then links
            return self.represent_mapping('tag:yaml.org,2002:map', [
                ('name', data['name']), 
                ('links', data['links'])
            ])
        elif 'name' in data and 'url' in data:
            # Order for link entries: name, then url
            return self.represent_mapping('tag:yaml.org,2002:map', [
                ('name', data['name']), 
                ('url', data['url'])
            ])
        # Default behavior for other dictionaries
        return self.represent_mapping('tag:yaml.org,2002:map', data.items())
    
    # Add the custom representer to the YAML dumper
    yaml.add_representer(dict, represent_dict_order)
    
    # Save results to YAML
    output_path = 'backend/scraper/data_links.yaml'
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        yaml.dump(result, f, allow_unicode=True, default_flow_style=False)
    
    print(f"\nSaved data links to {output_path}")
    print(f"Found {len(result)} categories")
    total_subcategories = sum(len(cat['subcategories']) for cat in result)
    print(f"Found {total_subcategories} subcategories with data links")
    total_links = sum(sum(len(subcat['links']) for subcat in cat['subcategories']) for cat in result)
    print(f"Found {total_links} total data links")
    
    return result


if __name__ == "__main__":
    main()