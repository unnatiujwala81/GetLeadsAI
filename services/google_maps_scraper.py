import re

import pandas as pd
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException, WebDriverException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

from services.website_scraper import WebsiteScraper


class GoogleMapsScraper:

    def __init__(self):
        options = webdriver.ChromeOptions()
        options.add_argument("--start-maximized")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--disable-notifications")
        options.add_argument("--disable-infobars")
        options.add_argument("--disable-extensions")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)

        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=options
        )
        self.driver.implicitly_wait(5)
        self.wait = WebDriverWait(self.driver, 15)
        self.website_scraper = WebsiteScraper()

    def _safe_text(self, by, selector, timeout=10):
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, selector))
            )
            return element.text.strip()
        except (TimeoutException, NoSuchElementException, WebDriverException):
            return ""

    def _safe_attribute(self, by, selector, attribute, timeout=10):
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, selector))
            )
            return element.get_attribute(attribute) or ""
        except (TimeoutException, NoSuchElementException, WebDriverException):
            return ""

    def _collect_business_urls(self, limit):
        results_panel = self.wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div[role='feed']"))
        )
        business_urls = []
        last_count = 0
        scroll_attempts = 0

        while len(business_urls) < limit and scroll_attempts < 10:
            anchors = results_panel.find_elements(By.CSS_SELECTOR, "a[href*='/maps/place/']")
            for anchor in anchors:
                href = anchor.get_attribute("href")
                if href and "/maps/place/" in href and href not in business_urls:
                    business_urls.append(href)

            if len(business_urls) >= limit:
                break

            if len(business_urls) == last_count:
                scroll_attempts += 1
            else:
                scroll_attempts = 0
                last_count = len(business_urls)

            self.driver.execute_script(
                "arguments[0].scrollTop = arguments[0].scrollHeight;",
                results_panel
            )

            try:
                WebDriverWait(self.driver, 10).until(
                    lambda d: len(
                        d.find_elements(By.CSS_SELECTOR, "a[href*='/maps/place/']")
                    ) > last_count
                )
            except TimeoutException:
                scroll_attempts += 1

        return business_urls[:limit]

    def _parse_reviews(self, text):
        if not text:
            return ""
        match = re.search(r"\(([\d,]+)\)", text)
        return match.group(1) if match else ""

    def _scrape_website_data(self, website):
        if not website or not website.startswith("http"):
            return {
                "Email": "",
                "Facebook": "",
                "Instagram": "",
                "LinkedIn": "",
                "YouTube": ""
            }

        try:
            return self.website_scraper.scrape(website)
        except Exception:
            return {
                "Email": "",
                "Facebook": "",
                "Instagram": "",
                "LinkedIn": "",
                "YouTube": ""
            }

    def search_businesses(self, category, location, limit=50):
        query = f"{category} in {location}"
        url = "https://www.google.com/maps/search/" + query.replace(" ", "+")
        businesses = []

        try:
            self.driver.get(url)
            self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div[role='feed']"))
            )
            business_urls = self._collect_business_urls(limit)

            for business_url in business_urls:
                try:
                    self.driver.get(business_url)
                    self.wait.until(
                        EC.presence_of_element_located(
                            (By.CSS_SELECTOR, "h1.DUwDvf, h1 span")
                        )
                    )

                    business_name = self._safe_text(By.CSS_SELECTOR, "h1.DUwDvf")
                    if not business_name:
                        business_name = self._safe_text(By.CSS_SELECTOR, "h1 span")

                    business_category = self._safe_text(By.CSS_SELECTOR, "button.DkEaL")
                    address = self._safe_text(By.CSS_SELECTOR, "button[data-item-id='address']")
                    if address.startswith("Address: "):
                        address = address.replace("Address: ", "").strip()

                    phone = self._safe_text(By.CSS_SELECTOR, "button[data-item-id^='phone']")
                    if phone.startswith("Phone: "):
                        phone = phone.replace("Phone: ", "").strip()

                    website = self._safe_attribute(
                        By.CSS_SELECTOR, "a[data-item-id='authority']", "href"
                    )

                    if not website:
                        website = self._safe_attribute(
                            By.CSS_SELECTOR, "a[href^='http']",
                            "href"
                        )

                    website_data = self._scrape_website_data(website)

                    rating = self._safe_text(
                        By.CSS_SELECTOR, "div.F7nice span[aria-hidden='true']"
                    )
                    if not rating:
                        rating = self._safe_text(By.CSS_SELECTOR, "span[class*='Aq14fc']")

                    reviews_text = self._safe_text(By.CSS_SELECTOR, "div.F7nice")
                    reviews = self._parse_reviews(reviews_text)

                    status = self._safe_text(By.CSS_SELECTOR, "span.ZDu9vd")

                    businesses.append({
                        "Business Name": business_name,
                        "Category": business_category,
                        "Address": address,
                        "Location": location,
                        "Phone Number": phone,
                        "Email": website_data.get("Email", ""),
                        "Website": website,
                        "Facebook": website_data.get("Facebook", ""),
                        "Instagram": website_data.get("Instagram", ""),
                        "LinkedIn": website_data.get("LinkedIn", ""),
                        "YouTube": website_data.get("YouTube", ""),
                        "Google Rating": rating,
                        "Reviews": reviews,
                        "Business Status": status,
                        "Google Maps URL": business_url,
                        "Notes": ""
                    })

                except Exception:
                    continue

        finally:
            self.driver.quit()

        columns = [
            "Business Name",
            "Category",
            "Address",
            "City",
            "State",
            "Country"
            "Phone Number",
            "Email",
            "Website",
            "Facebook",
            "Instagram",
            "LinkedIn",
            "YouTube",
            "Google Rating",
            "Reviews",
            "Business Status",
            "Google Maps URL",
            "Notes"
        ]
        df = pd.DataFrame(businesses, columns=columns)

        if not df.empty:
            df.drop_duplicates(subset=["Business Name"], inplace=True)

        return df
        