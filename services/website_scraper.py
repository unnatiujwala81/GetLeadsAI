import re
import requests
from bs4 import BeautifulSoup


class WebsiteScraper:

    def scrape(self, website):

        data = {
            "Email": "",
            "Facebook": "",
            "Instagram": "",
            "LinkedIn": "",
            "YouTube": ""
        }

        if not website:
            return data

        try:
            headers = {
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 Chrome/137.0 Safari/537.36"
                )
            }

            response = requests.get(
                website,
                headers=headers,
                timeout=10
            )

            html = response.text

            soup = BeautifulSoup(html, "html.parser")

            # -----------------------
            # Email
            # -----------------------

            emails = re.findall(
                r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}",
                html
            )

            if emails:
                data["Email"] = emails[0]

            # -----------------------
            # Social Links
            # -----------------------

            for link in soup.find_all("a", href=True):

                href = link["href"]

                if "facebook.com" in href and not data["Facebook"]:
                    data["Facebook"] = href

                elif "instagram.com" in href and not data["Instagram"]:
                    data["Instagram"] = href

                elif "linkedin.com" in href and not data["LinkedIn"]:
                    data["LinkedIn"] = href

                elif "youtube.com" in href and not data["YouTube"]:
                    data["YouTube"] = href

        except Exception:
            pass

        return data