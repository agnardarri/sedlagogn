import os
import yaml
import requests
import urllib.parse
from pathlib import Path

def download_subcategory_data(subcategory_name, yaml_path='backend/scraper/data_links.yaml', cache_dir='backend/cache'):
    """
    Download all data files for a specified subcategory name and save them to cache.
    
    Args:
        subcategory_name (str): Name of the subcategory to download data for
        yaml_path (str): Path to the data_links.yaml file
        cache_dir (str): Directory where downloaded files will be stored
        
    Returns:
        dict: A summary of the download operation, including successful and failed downloads
    """
    print(f"Looking for subcategory: {subcategory_name}")
    
    # Create cache directory if it doesn't exist
    os.makedirs(cache_dir, exist_ok=True)

    ROOT = "https://www.sedlabanki.is"
    
    # Load data_links.yaml
    try:
        with open(yaml_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
    except Exception as e:
        print(f"Error loading {yaml_path}: {str(e)}")
        return {"error": f"Failed to load {yaml_path}: {str(e)}"}
    
    if not data:
        print(f"No data found in {yaml_path}")
        return {"error": f"No data found in {yaml_path}"}
    
    # Find the specified subcategory
    matches = []
    for category in data:
        for subcategory in category['subcategories']:
            if subcategory['name'] == subcategory_name:
                matches.append({
                    'category': category['category'],
                    'subcategory': subcategory['name'],
                    'links': subcategory['links']
                })
    
    if not matches:
        print(f"No subcategory found with name: {subcategory_name}")
        return {"error": f"Subcategory '{subcategory_name}' not found"}
    
    # Initialize result summary
    result = {
        "subcategory": subcategory_name,
        "matches": len(matches),
        "downloaded_files": [],
        "failed_downloads": []
    }
    
    # Process each match
    for match in matches:
        category_name = match['category']
        subcategory_name = match['subcategory']
        links = match['links']
        
        print(f"Found {subcategory_name} in category {category_name} with {len(links)} links")
        
        # Download files from each link
        for link in links:
            link_name = link['name']
            link_url = link['url']
            
            # Ensure URL is absolute with ROOT
            if not link_url.startswith('http'):
                link_url = f"{ROOT}{link_url if link_url.startswith('/') else '/' + link_url}"
            
            print(f"  Downloading: {link_name} from {link_url}")
            
            try:
                # Download file
                response = requests.get(link_url, verify=False, timeout=30)
                response.raise_for_status()
                
                # Determine filename
                if "Content-Disposition" in response.headers:
                    # Extract filename from header if available
                    content_disposition = response.headers["Content-Disposition"]
                    filename = content_disposition.split("filename=")[1].strip('"')
                else:
                    # Use the last part of the URL path as filename
                    filename = os.path.basename(urllib.parse.urlparse(link_url).path)
                    # If empty or no extension, use the link name with a default extension
                    if not filename or '.' not in filename:
                        filename = f"{link_name.replace(' ', '_')}.xlsx"
                
                # Save directly to the flat cache directory
                file_path = os.path.join(cache_dir, filename)
                
                # Ensure unique filename by adding a number if it already exists
                counter = 1
                name, ext = os.path.splitext(filename)
                while os.path.exists(file_path):
                    filename = f"{name}_{counter}{ext}"
                    file_path = os.path.join(cache_dir, filename)
                    counter += 1
                
                # Save the file
                with open(file_path, 'wb') as f:
                    f.write(response.content)
                
                print(f"  Saved to {file_path}")
                
                # Add to successful downloads
                result["downloaded_files"].append({
                    "name": link_name,
                    "url": link_url,
                    "path": file_path
                })
                
            except Exception as e:
                error_msg = f"Failed to download {link_name} from {link_url}: {str(e)}"
                print(f"  Error: {error_msg}")
                
                # Add to failed downloads
                result["failed_downloads"].append({
                    "name": link_name,
                    "url": link_url,
                    "error": str(e)
                })
    
    # Print summary
    print(f"\nDownload summary for {subcategory_name}:")
    print(f"  Found in {len(matches)} categories")
    print(f"  Successfully downloaded {len(result['downloaded_files'])} files")
    print(f"  Failed to download {len(result['failed_downloads'])} files")
    
    return result


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python download_data.py <subcategory_name>")
        sys.exit(1)
    
    subcategory_name = sys.argv[1]
    download_subcategory_data(subcategory_name) 