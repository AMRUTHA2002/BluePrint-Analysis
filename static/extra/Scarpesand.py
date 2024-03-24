import requests
from bs4 import BeautifulSoup
import pandas as pd
import re

# Send an HTTP request to the website
url = "https://dir.indiamart.com/impcat/sand.html"
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
    
    Sand = element.find(class_="pnm ldf cur").get_text(strip=True) if element.find(class_="pnm ldf cur") else None
    price = element.find(class_="prc cur").get_text(strip=True) if element.find(class_="prc cur") else None


    if price is not None:
        parts = price.split('/')
        result = parts[0].strip()
        Quantity=parts[1].strip().replace("Get Latest Price","")

        R_result=result.split('₹')
        Price_match=float(R_result[1].strip().replace(",",""))

    text = element.find(class_="desc des_p elps3l").get_text(strip=True) if element.find(class_="desc des_p elps3l") else None
    
    form_match = re.search(r'Form:\s+(\w+)', text)
    if form_match is not None:
        form=form_match.group(1)
    else:
        form=None

    color_match = re.search(r'Color:\s+(\w+)', text)
    if color_match is not None:
        color=color_match.group(1)
    else:
        color=None

    material_match = re.search(r'Material:\s+(\w+)', text)
    if material_match is not None:
        material=material_match.group(1)
    else:
        material=None

    # Append the extracted data to the list
    data_list.append({
        'Name': Sand,
        'Price': Price_match,
        'Quantity':Quantity,
        'Form': form,
        'Color': color,
        'Material':material

    })

# Create a DataFrame (table) using pandas
df = pd.DataFrame(data_list)

# Print the table
print(df)
file_name = f'Scrape_Sand.xlsx'
df.to_excel(excel_writer=f'C:/Users/Ansika Babu/Downloads/DASHBOARD/DASHBOARD/static/extra/{file_name}', index=False)
