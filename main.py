import selenium
import bs4
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
import requests
import json

WEBHOOK = "https://discord.com/api/webhooks/1397904877857800192/42Fe_nz83sxEjjoUVvaVpbqNzLhjq60KPxE9CQYa5iCcMhh_Tsjl8uLnhor9y23ZHJLG"
SREALITY_QUERY = "https://www.sreality.cz/hledani/pronajem/byty?velikost=2%2B1%2C3%2B1%2C3%2Bkk&region=Brno&region-id=5740&region-typ=municipality&noredirect=1"
BEZREALITKY_QUERY = "https://www.bezrealitky.cz/vyhledat?offerType=PRONAJEM&estateType=BYT&disposition=DISP_2_1&disposition=DISP_3_KK&disposition=DISP_3_1&regionOsmIds=R438171&osm_value=Brno%2C+okres+Brno-m%C4%9Bsto%2C+Jihomoravsk%C3%BD+kraj%2C+Jihov%C3%BDchod%2C+%C4%8Cesko&roommate=false&location=exact&currency=CZK"
SREALITY_LISTING_COUNT = 24
BEZREALITKY_LISTING_COUNT = 15

def scrapeSREALITY(driver, listings: list):
    print("Opening SREALITY page with Selenium...")
    driver.get(SREALITY_QUERY)
    
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
            if listing["header"].startswith("TIP"):
                continue  # Skip ads"
            if "adurl=" in listing["link"]:
                continue  # Skip ads with adurl
            if listing["id"] == "No ID":
                continue
            listings.append(listing)
    return listings

def scrapeBEZREALITKY(driver, listings: list):
    print("Opening BEZREALITKY page with Selenium...")
    driver.get(BEZREALITKY_QUERY)
    for i in range(1, BEZREALITKY_LISTING_COUNT + 1):
        elements = driver.find_elements(By.XPATH, f"/html/body/div[1]/main/section/div/div[2]/div/div[6]/section[1]/article[{i}]/div[2]")
        if elements:
            text = elements[0].text.strip().split("\n")
            href_element = driver.find_elements(By.XPATH, f"/html/body/div[1]/main/section/div/div[2]/div/div[6]/section[1]/article[{i}]/div[2]/h2/a")
            href = href_element[0].get_attribute("href") if href_element else "No Link"
            listing = {
                "header": f"{text[0]} {text[2]} {text[3]}" if len(text) > 3 else "Untitled Listing",
                "Address": text[1] if len(text) > 1 else "No Address",
                "Price": text[5] + text[6] if len(text) > 6 else "No Price",
                "link": href if href else "No Link",
                "id": href.split("/")[-1].split("-")[0] if href and href != "No Link" else "No ID"
            }
            
            listings.append(listing)
            
    return listings

def remove_seen_listings(listings: list, seen_file: str = "seen.json"):
    try:
        with open(seen_file, "r", encoding="utf-8") as f:
            seen = json.load(f)
    except FileNotFoundError:
        seen = []

    seen_ids = [item["id"] for item in seen]
    new_listings = [listing for listing in listings if listing["id"] not in seen_ids]
    
    with open(seen_file, "w", encoding="utf-8") as f:
        json.dump(listings, f, ensure_ascii=False, indent=2)

    return new_listings

def main():
    foundlistings = []
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36")
    
    driver = webdriver.Firefox(options=options)
    scrapeSREALITY(driver, foundlistings)
    scrapeBEZREALITKY(driver, foundlistings)
    foundlistings = remove_seen_listings(foundlistings)
    print(f"Found {len(foundlistings)} new listings.")
    for i in foundlistings:
        requests.post(WEBHOOK, json={
            "content": f"{i['header']}\n{i['Price']}\n{i['Address']}\n{i['link']}"
        })
    driver.quit()

if __name__ == "__main__":
    main()