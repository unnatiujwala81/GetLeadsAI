import time
import pandas as pd

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from webdriver_manager.chrome import ChromeDriverManager

from services.website_scraper import WebsiteScraper

class GoogleMapsScraper:

    def __init__(self):

        options = webdriver.ChromeOptions()

        options.add_argument("--start-maximized")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--disable-notifications")

        self.driver = webdriver.Chrome(
            service=Service(
                ChromeDriverManager().install()
            ),
            options=options
        )

        self.driver.implicitly_wait(10)
        self.wait = WebDriverWait(self.driver, 15)

        self.website_scraper = WebsiteScraper()

    def search_businesses(self, category, location, limit=50):

        query = f"{category} in {location}"

        url = "https://www.google.com/maps/search/" + query.replace(" ", "+")

        self.driver.get(url)

        self.wait.until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "div[role='feed']")
            )
        )

        results_panel = self.driver.find_element(
            By.CSS_SELECTOR,
            "div[role='feed']"
        )

        previous_count = 0

        while True:

            cards = self.driver.find_elements(
                By.CSS_SELECTOR,
                "a[href*='/maps/place/']"
            )

            print(f"Found {len(cards)} businesses")

            if len(cards) >= limit:
                break

            if len(cards) == previous_count:
                break

            previous_count = len(cards)

            self.driver.execute_script(
                "arguments[0].scrollTop = arguments[0].scrollHeight",
                results_panel
            )

            time.sleep(2)

        cards = self.driver.find_elements(
            By.CSS_SELECTOR,
            "a[href*='/maps/place/']"
        )

        businesses = []

        for card in cards[:limit]:

            try:

                self.driver.execute_script(
                    "arguments[0].click();",
                    card
                )

                time.sleep(3)

                try:
                   business_name = self.wait.until(
                       EC.presence_of_element_located(
                           (By.CSS_SELECTOR, "h1.DUwDvf")
                       )
                   ).text
                except:
                    business_name = ""

                try:
                    business_category = self.driver.find_element(
                        By.CSS_SELECTOR,
                        "button.DkEaL"
                    ).text
                except:
                    business_category = ""

                try:
                    address = self.driver.find_element(
                        By.CSS_SELECTOR,
                        "button[data-item-id='address']"
                    ).text.replace("Address: ", "")
                except:
                    address = ""

                try:
                    phone = self.driver.find_element(
                        By.CSS_SELECTOR,
                        "button[data-item-id^='phone']"
                    ).text.replace("Phone: ", "")
                except:
                    phone = ""

                try:
                    website = self.driver.find_element(
                        By.CSS_SELECTOR,
                        "a[data-item-id='authority']"
                    ).get_attribute("href")
                except:
                    website = ""

                try:
                    website_data = self.website_scraper.scrape(website)
                except Exception as e:
                    print("Website scraper failed:", website)
                    print(e)

                    website_data = {
                    "Email": "",
                    "Facebook": "",
                    "Instagram": "",
                    "LinkedIn": "",
                    "YouTube": ""
                    }

                try:
                    rating = self.driver.find_element(
                        By.CSS_SELECTOR,
                        "div.F7nice span[aria-hidden='true']"
                    ).text
                except:
                    rating = ""

                try:
                    reviews_text = self.driver.find_element(
                        By.CSS_SELECTOR,
                        "div.F7nice"
                    ).text

                    # Example:
                    # "4.8 (215)"
                    # Extracts: 215

                    import re

                    match = re.search(
                        r"\(([\d,]+)\)",
                        reviews_text
                    )

                    if match:
                        reviews = match.group(1)
                    else:
                        reviews = ""

                except:
                    reviews = ""

                try:
                    status = self.driver.find_element(
                        By.CSS_SELECTOR,
                        "span.ZDu9vd"
                    ).text
                except:
                    status = ""

                maps_url = self.driver.current_url

                businesses.append({
                    "Business Name": business_name,
                    "Category": business_category,
                    "Address": address,
                    "Location": location,
                    "Phone": phone,
                    "Email": website_data["Email"],
                    "Website": website,
                    "Facebook": website_data["Facebook"],
                    "Instagram": website_data["Instagram"],
                    "LinkedIn": website_data["LinkedIn"],
                    "YouTube": website_data["YouTube"],
                    "Google Rating": rating,
                    "Reviews": reviews,
                    "Business Status": status,
                    "Google Maps URL": maps_url,
                    "Notes": ""
                })

                print(f"✓ {business_name}")

            except Exception as e:
                print("Error:", e)

        self.driver.quit()

        df = pd.DataFrame(businesses)

        if not df.empty:
            df.drop_duplicates(
                subset=["Business Name"],
                inplace=True
            )

        return df
