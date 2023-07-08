import requests
from bs4 import BeautifulSoup
import csv
import time
import re

# # Part 1: Scrape product details from product listing pages

# # Define the URL pattern with page number as a placeholder
url_pattern = "https://www.amazon.in/s?k=bags&crid=2M096C61O4MLT&qid=1653308124&sprefix=ba%2Caps%2C283&ref=sr_pg_{}"

# Number of pages to scrape
num_pages = 20

# Lists to store the scraped data
product_urls = []
product_data = []

# Scrape the product listing pages
for page in range(1, num_pages + 1):
    # Construct the URL for the current page
    url = url_pattern.format(page)

    # Send a GET request to the page URL
    response = requests.get(url)

    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(response.content, "html.parser")

    # Extracting the product details from the page
    results = soup.find_all("div", {"data-component-type": "s-search-result"})
    for result in results:
        # Extracting product URL
        product_url = result.find("a", {"class": "a-link-normal s-no-outline"}).get("href")[1:]
        product_urls.append(product_url)

        # Extract other product details
        product_name = result.find("span", {"class": "a-size-medium a-color-base a-text-normal"})
        product_price = result.find("span", {"class": "a-price-whole"})
        rating = result.find("span", {"class": "a-icon-alt"})
        num_reviews = result.find("span", {"class": "a-size-base"})


        # Check if the fields exist before extracting the text
        if product_name:
            product_name = product_name.text.strip()
        if product_price:
            product_price = product_price.text.strip().replace(",", "")
        if rating:
            rating = rating.text.split()[0]
        if num_reviews:
            num_reviews = num_reviews.text.strip().replace(",", "")

        # Store the data in a dictionary
        product_data.append({
            "Product URL": product_url,
            "Product Name": product_name,
            "Product Price": product_price,
            "Rating": rating,
            "Number of Reviews": num_reviews
        })


# Part 2: Fetch additional information from each product page

# Maximum number of product URLs to fetch
max_urls = 200

# List to store the fetched data
fetched_data = []

asin = None
# Fetching additional information from each product page
for product_url in product_urls[:max_urls]:
    # Sending a GET request to the product URL
    
    try:
        product_response = requests.get(f"https://www.amazon.in/{product_url}")
        product_soup = BeautifulSoup(product_response.content, "html.parser")

        # Extracting additional information from the product page
        description = product_soup.find("div", {"id": "productDescription"})

        asin = product_url.split("/dp/")[1].split("/")[0]

        # Storing the fetched data in a dictionary

        fetched_data.append({
            "Product URL": product_url,
            "Description": description.get_text(strip=True) if description else None,
            "ASIN": asin,
            
        })

    except requests.exceptions.RequestException as e:
        print(f"Error encountered while fetching data for URL: {product_url}")
        print(f"Error message: {str(e)}")
        continue

    # time.sleep(1)

# Merging the fetched data with the product data
for i in range(len(product_data)):
    product_data[i].update(fetched_data[i])

# Exporting the data to a CSV file
fields = ["Product URL", "Product Name", "Product Price", "Rating", "Number of Reviews",
          "Description", "ASIN"]

filename = "product_data.csv"
with open(filename, "w", newline="", encoding="utf-8") as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=fields)
    writer.writeheader()
    writer.writerows(product_data)

print("Data exported successfully to", filename)