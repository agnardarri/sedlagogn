import os
import yaml
from bs4 import BeautifulSoup
import requests
import urllib3
from datetime import datetime
import dateparser

# Suppress only the specific InsecureRequestWarning
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def parse_icelandic_date(date_str):
    """Parse Icelandic dates using dateparser"""
    if not date_str or date_str.strip() == "":
        return None
    
    # Use dateparser with Icelandic language settings
    parsed_date = dateparser.parse(
        date_str.replace('\xa0', ' ').strip(),
        languages=['is'],
        settings={'DATE_ORDER': 'DMY'}
    )
    
    return parsed_date.strftime('%Y-%m-%d') if parsed_date else None

def main():
    # Scrape data from main page
    page = requests.get("https://www.sedlabanki.is/hagtolur/talnaefni", verify=False)
    soup = BeautifulSoup(page.content, 'html.parser')
    result = []
    
    # Process each category
    for h4 in soup.find('div', class_='newslist').find_all('h4', class_='htitle'):
        category = {
            'category': h4.text.strip(),
            'subcategories': []
        }
        
        # Process rows in the table
        table = h4.find_next('table')
        for row in table.find_all('tr')[1:]:  # Skip header row
            cells = row.find_all('td')
            if len(cells) < 6:  # Need at least 6 cells
                continue
            
            # Get link and dates
            anchor = cells[0].find('a')
            if not anchor:
                continue
                
            # Build entry
            category['subcategories'].append({
                'name': anchor.get_text(strip=True),
                'url': anchor['href'],
                'last_update': parse_icelandic_date(cells[3].get_text(strip=True)),
                'next_update': parse_icelandic_date(cells[5].get_text(strip=True))
            })
        
        # Add category if it has entries
        if category['subcategories']:
            result.append(category)
    
    # Define field order representer
    def represent_dict_order(self, data):
        if 'category' in data:
            return self.represent_mapping('tag:yaml.org,2002:map', 
                [('category', data['category']), ('subcategories', data['subcategories'])])
        elif 'name' in data:
            return self.represent_mapping('tag:yaml.org,2002:map',
                [(k, data[k]) for k in ['name', 'url', 'last_update', 'next_update'] if k in data])
        return self.represent_mapping('tag:yaml.org,2002:map', data.items())
    
    # Save to YAML
    output_path = 'backend/scraper/page_links.yaml'
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    yaml.add_representer(dict, represent_dict_order)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        yaml.dump(result, f, allow_unicode=True, default_flow_style=False)
    
    # Print summary
    print(f"\nSaved {len(result)} categories with {sum(len(cat['subcategories']) for cat in result)} subcategories to {output_path}")

if __name__ == "__main__":
    main() 