from scraper import ScraperConfig

novinite_config = ScraperConfig(
    name="novinite.com",
    base_url="https://www.novinite.com",
    item_selector="div.item",
    title_selector="h2 a",
    link_selector="h2 a",
    summary_selector="p",
    category_selector="div.date a",
    date_selector="div.date",
    content_selector="div#textsize"
)
