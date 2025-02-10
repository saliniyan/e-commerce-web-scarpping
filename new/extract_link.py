import json

# Read data from JSON file
with open("new/POS_STAGING.products-1.json", "r") as file:
    data = json.load(file)

links = [item["name"] for item in data if "name" in item]

# Store links in a list
product_links = links

# Save links to a new JSON file
with open("new/product_names.json", "w") as outfile:
    json.dump(product_links, outfile, indent=4)
