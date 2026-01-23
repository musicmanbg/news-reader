from scraper import ScraperConfig

novinite_config = ScraperConfig(
    name="Novinite",
    base_url="https://www.novinite.com",
    item_selector="div.item",
    title_selector="div.text h2 a",
    link_selector="div.text h2 a",
    summary_selector="div.text p",
    category_selector="div.date a",
    date_selector="div.date"
)

# We can add more here later
# bta_config = ScraperConfig(...)
