import pandas as pd
import json
from datetime import datetime
import os
from pathlib import Path
import numpy as np

def extract_nested_json(file_path, config):
    """Extract nested JSON structure from Excel file based on config."""
    sheet_config = config["sheets"][0]
    sheet_name = sheet_config["sheet"]
    
    # Read the Excel file
    df = pd.read_excel(file_path, sheet_name=sheet_name, header=None)
    
    # Extract dates from date row
    date_row = sheet_config["date_row"] - 1  # Convert to 0-based index
    dates = []
    for col in range(sheet_config["data_start_column"] - 1, df.shape[1]):
        cell_value = df.iloc[date_row, col]
        if pd.notna(cell_value):
            if isinstance(cell_value, (datetime, pd.Timestamp)):
                dates.append(cell_value.strftime("%Y-%m-%d"))
            else:
                dates.append(str(cell_value))
    
    # Define parsing function for each section
    def parse_section(start_row, hierarchy_levels, section_name):
        result = {"name": section_name, "children": []}
        
        # Stack to track parent nodes at each level
        # Each entry is (node, level)
        stack = [(result, 0)]
        
        current_row = start_row
        for level in hierarchy_levels:
            # Get data for current row
            name_col = sheet_config["data_name_column"] - 1
            row_data = df.iloc[current_row]
            
            # Skip rows with no data
            if pd.isna(row_data[name_col]):
                current_row += 1
                continue
                
            name = str(row_data[name_col]).strip()
            
            # Handle translations if names contain "/"
            icelandic_name = name
            english_name = name
            if "/" in name:
                parts = name.split("/", 1)
                icelandic_name = parts[0].strip()
                english_name = parts[1].strip()
            
            # Prepare values
            values = {}
            for i, date in enumerate(dates):
                col_idx = sheet_config["data_start_column"] - 1 + i
                if col_idx < df.shape[1]:
                    val = row_data[col_idx]
                    if pd.notna(val):
                        if isinstance(val, (np.integer, np.floating)):
                            val = float(val)
                        values[date] = val
            
            # Create node
            node = {
                "name": name,
                "is": icelandic_name,
                "en": english_name,
                "values": values,
                "children": []
            }
            
            # Find correct parent in stack
            while stack[-1][1] >= level:
                stack.pop()
            
            # Add to parent and push to stack
            stack[-1][0]["children"].append(node)
            stack.append((node, level))
            
            current_row += 1
        
        return result
    
    # Parse assets section
    assets_row = sheet_config["assets_row"] - 1  # Convert to 0-based index
    assets = parse_section(
        assets_row, 
        sheet_config["assets_hierarchy"], 
        "EIGNIR / ASSETS"
    )
    
    # Parse liabilities section
    liabilities_row = sheet_config["liabilities_row"] - 1  # Convert to 0-based index
    liabilities = parse_section(
        liabilities_row, 
        sheet_config["liabilities_hierarchy"], 
        "SKULDIR / LIABILITIES"
    )
    
    # Create final result
    result = {
        "metadata": {
            "file": os.path.basename(file_path),
            "sheet": sheet_name,
            "dates": dates,
            "extracted_at": datetime.now().isoformat()
        },
        "data": {
            "assets": assets,
            "liabilities": liabilities
        }
    }
    
    return result

if __name__ == "__main__":
    # Configuration from your JSON
    config = {
        "sheets": [
            {
                "sheet": "I",
                "date_row": 9,
                "data_start_column": 2,
                "data_name_column": 1,
                "assets_row": 10,
                "liabilities_row": 29,
                "assets_hierarchy": [
                    1, 2, 3, 4, 5, 5, 4, 5, 5, 5, 3, 2, 3, 3, 4, 4, 4, 3
                ],
                "liabilities_hierarchy": [
                    1, 2, 3, 3, 3, 3, 4, 5, 5, 5, 4, 5, 5, 5, 2, 3, 3, 3, 4, 4
                ]
            }
        ]
    }
    
    # Extract data from file
    file_path = "backend/cache/INN_ReikningarBankakerfis_012025.xlsx"
    result = extract_nested_json(file_path, config)
    
    # Save as JSON
    output_dir = Path("backend/parsed_data")
    output_dir.mkdir(exist_ok=True)
    
    output_file = output_dir / "banking_system_accounts.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"Extracted nested JSON saved to {output_file}")
    
    # Display first few nodes of each section
    print("\nAssets top-level items:")
    for child in result["data"]["assets"]["children"]:
        print(f"- {child['name']}")
        if child.get("children"):
            for subchild in child["children"][:2]:  # Show only first 2 children
                print(f"  └─ {subchild['name']}")
                if len(child["children"]) > 2:
                    print(f"  └─ ... and {len(child['children'])-2} more")
    
    print("\nLiabilities top-level items:")
    for child in result["data"]["liabilities"]["children"]:
        print(f"- {child['name']}")
        if child.get("children"):
            for subchild in child["children"][:2]:  # Show only first 2 children
                print(f"  └─ {subchild['name']}")
                if len(child["children"]) > 2:
                    print(f"  └─ ... and {len(child['children'])-2} more") 