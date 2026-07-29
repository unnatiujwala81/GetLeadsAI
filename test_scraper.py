from services.google_maps_scraper import GoogleMapsScraper


scraper = GoogleMapsScraper()


results = scraper.search_businesses(
    "Dentist",
    "Texas USA",
    20
)


print(results)

results.to_csv(
    "leads.csv",
    index=False
)