import requests
from bs4 import BeautifulSoup
import pandas as pd
import re

# Send an HTTP request to the website
url = "https://dir.indiamart.com/impcat/construction-aggregates.html"
response = requests.get(url)

# Parse the HTML content using Beautiful Soup
soup = BeautifulSoup(response.text, 'html.parser')

# Extract information based on class name
class_name_to_find = "rht pnt flx"

# Find all elements with the specified class name
elements = soup.find_all(class_=class_name_to_find)

# Initialize an empty list to store the extracted data
data_list = []

for element in elements:
    # Extract data from sub-classes within each element
    
    Steel = element.find(class_="pnm ldf cur").get_text(strip=True) if element.find(class_="pnm ldf cur") else None
    price_element = element.find(class_="prc cur")
    if price_element:
        price = price_element.get_text(strip=True)
        parts = price.split('/')
        result = parts[0].strip()
        Quantity = parts[1].strip().replace("Get Latest Price", "")

        R_result = result.split('₹')
        try:
            Price_match = float(R_result[1].strip().replace(",", ""))
        except ValueError:
            Price_match = None
            print(f"Failed to convert price to float: {price}")

        print(Price_match)

        text = element.find(class_="desc des_p elps3l").get_text(strip=True) if element.find(
            class_="desc des_p elps3l") else None

        brand_match = re.search(r'Brand:\s+(\w+)', text)
        brand = brand_match.group(1) if brand_match else None

        grade_match = re.search(r'Grade:\s+(\w+)', text)
        grade = grade_match.group(1) if grade_match else None

        material_match = re.search(r'Material:\s+(\w+)', text)
        material = material_match.group(1) if material_match else None

        # Append the extracted data to the list
        data_list.append({
            'Name': Steel,
            'Price': Price_match,
            'Quantity': Quantity,
            'Brand': brand,
            'Material': material
        })

# Create a DataFrame (table) using pandas
df = pd.DataFrame(data_list)

# Print the table
print(df)

file_name = 'Scrape_aggregates.xlsx'
df.to_excel(excel_writer=f'C:/Users/Ansika Babu/Downloads/DASHBOARD/DASHBOARD/static/extra/{file_name}', index=False)
