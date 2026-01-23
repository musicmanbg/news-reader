from typing import List, Optional
import requests
from bs4 import BeautifulSoup
from pydantic import BaseModel, HttpUrl


class ScraperConfig(BaseModel):
    name: str
    base_url: str
    item_selector: str
    title_selector: str
    link_selector: str
    summary_selector: Optional[str] = None
    category_selector: Optional[str] = None
    date_selector: Optional[str] = None


class Article(BaseModel):
    title: str
    url: str
    summary: Optional[str] = None
    category: Optional[str] = None
    date: Optional[str] = None
    source: str


class NewsScraper:
    def __init__(self, config: ScraperConfig):
        self.config = config
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

    def scrape(self, url: str) -> List[Article]:
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, "html.parser")
        items = soup.select(self.config.item_selector)
        
        articles = []
        for item in items:
            try:
                title_elem = item.select_one(self.config.title_selector)
                link_elem = item.select_one(self.config.link_selector)
                
                if not title_elem or not link_elem:
                    continue
                
                title = title_elem.get_text(strip=True)
                link = link_elem.get("href")
                
                if not link.startswith("http"):
                    link = f"{self.config.base_url.rstrip('/')}/{link.lstrip('/')}"
                
                summary = None
                if self.config.summary_selector:
                    summary_elem = item.select_one(self.config.summary_selector)
                    if summary_elem:
                        summary = summary_elem.get_text(strip=True)
                
                category = None
                if self.config.category_selector:
                    category_elem = item.select_one(self.config.category_selector)
                    if category_elem:
                        category = category_elem.get_text(strip=True)

                date = None
                if self.config.date_selector:
                    date_elem = item.select_one(self.config.date_selector)
                    if date_elem:
                        # Sometimes date is inside text but we just want the text for now
                        date = date_elem.get_text(strip=True)

                articles.append(Article(
                    title=title,
                    url=link,
                    summary=summary,
                    category=category,
                    date=date,
                    source=self.config.name
                ))
            except Exception as e:
                print(f"Error parsing item: {e}")
                continue
                
        return articles
