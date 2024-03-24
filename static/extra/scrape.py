from selenium.webdriver.firefox.service import Service
from selenium import webdriver
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.firefox.options import Options
import requests
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time
import pandas as pd
from tkinter import messagebox
from datetime import datetime
import os

service = ''
try:
    service = Service(executable_path=GeckoDriverManager().install())
except:
    service = Service(executable_path=r'geckodriver.exe')
    print('Old selenium in execution.')

fp = Options()
driver = webdriver.Firefox(options=fp, service=service)

try:
    fp.binary_location = r'C:\Program Files\Mozilla Firefox\firefox.exe'
except:
    fp.binary_location = r'C:\Program Files (x86)\Mozilla Firefox\firefox.exe'

date_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
file_name = f'Scrape_Cement.xlsx'
file_path = f'C:/Users/Ansika Babu/Downloads/FLASKAPP/FLASK/static/extra/{file_name}'
def scrape_cement_prices():

    url = "https://inampro.nic.in/live-prices-of-opc-and-ppc-and-srpc-cement.htm"
    driver.get(url)
    i=0
    next_xpath = '//*[@id="Example_next"]'
    data = []
    while i<3:
        time.sleep(2)   
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        table = soup.find("table", {"id": "Example"})
        if table:
            for row in table.find_all("tr"):
                cells = row.find_all("td")
                row_data = [cell.get_text(strip=True) for cell in cells]
                if row_data:
                    data.append(row_data)           
            i+=1
        else:
            #st.warning("Table not found with the specified ID.")
            print("Table not found with the specified ID")   
        driver.find_element(By.XPATH,next_xpath).click()    
    #print(row_data)
    print(data)
    df = pd.DataFrame(data,columns=["Sr.No","Seller","Plant","Product","Packaging","Ceiling Price","Offer Price"])
    print(df)
    df.to_excel(excel_writer=file_path, index=False)
    messagebox.showinfo("Success",f"Output file created at {os.path.abspath(file_name)}")
if __name__ == "__main__":
    scrape_cement_prices()