from src.news_reader.scraper import NewsScraper
from src.news_reader.configs import novinite_config
import json

def test_novinite():
    url = "https://www.novinite.com/archives/2025-12-28"
    scraper = NewsScraper(novinite_config)
    articles = scraper.scrape(url)
    
    print(f"Scraped {len(articles)} articles from {url}")
    for i, article in enumerate(articles[:5]):
        print(f"\nArticle {i+1}:")
        print(f"Title: {article.title}")
        print(f"URL: {article.url}")
        print(f"Category: {article.category}")
        print(f"Summary: {article.summary[:100]}..." if article.summary else "No summary")

if __name__ == "__main__":
    test_novinite()
