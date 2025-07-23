import selenium
import bs4
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By

SREALITY_QUERY = "https://www.sreality.cz/hledani/pronajem/byty?velikost=2%2B1%2C3%2B1%2C3%2Bkk&region=Brno&region-id=5740&region-typ=municipality&noredirect=1"
SREALITY_LISTING_COUNT = 24

def scrapeSREALITY(driver, listings: list):
    print("Opening SREALITY page with Selenium...")
    driver.get(SREALITY_QUERY)
    html = driver.page_source
    
    with open("sreality_dump.html", "w", encoding="utf-8") as f:
        f.write(html)
    
    
    # Use Selenium to find elements by XPath
    for i in range(1, SREALITY_LISTING_COUNT + 1):
        elements = driver.find_elements(By.XPATH, f"/html/body/div[1]/div[3]/div[1]/div[2]/ul/li[{i}]/a")
        if elements:
            text = elements[0].text.strip().split("\n")
            href = elements[0].get_attribute("href")
            listing = {
                "header": text[0] if len(text) > 0 else "Untitled Listing",
                "Address": text[1] if len(text) > 1 else "No Address",
                "Price": text[2] if len(text) > 2 else "No Price",
                "link": href if href else "No Link",
                "id": href.split("/")[-1] if href else "No ID"
            }
            listings.append(listing)
            

def main():
    foundlistings = []
    options = Options()
    # options.add_argument("--headless")
    options.set_preference("javascript.enabled", False)
    driver = webdriver.Firefox(options=options)
    foundlistings.append(scrapeSREALITY(driver, foundlistings))
    
    
    driver.quit()

if __name__ == "__main__":
    main()