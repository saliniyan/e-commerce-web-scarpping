import json
import re

# Read data from JSON file
with open("new/POS_STAGING.products-1.json", "r") as file:
    data = json.load(file)

# Function to extract weight if present
def extract_weight(name):
    match = re.search(r'\b(\d+\s*(?:GM|G|KG|ML|L))\b', name, re.IGNORECASE)
    return match.group(1) if match else None

# Function to remove weight from name
def remove_weight(name):
    return re.sub(r'\b\d+\s*(?:GM|G|KG|ML|L)\b', '', name, flags=re.IGNORECASE).strip()

# Function to clean up product names further
def clean_name(name):
    name = remove_weight(name)
    return re.sub(r'[-\s]+$', '', name)  # Remove trailing hyphens and spaces

# Process data
products = []
for item in data:
    if "name" in item:
        name = clean_name(item["name"])
        weight = extract_weight(item["name"])
        products.append({"name": name, "weight": weight})

# Save processed data to a new JSON file
with open("new/product_details.json", "w") as outfile:
    json.dump(products, outfile, indent=4)
