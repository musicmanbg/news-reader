import json
import functions_framework
from scraper import NewsScraper
from configs import novinite_config

@functions_framework.http
def scrape_news_http(request):
    """
    HTTP Cloud Function to scrape news.
    """
    try:
        scraper = NewsScraper(novinite_config)
        articles = scraper.scrape(novinite_config.base_url)
        
        # Convert pydantic models to dicts
        articles_data = [article.model_dump() for article in articles]
        
        return json.dumps(articles_data), 200, {'Content-Type': 'application/json'}
    except Exception as e:
        return json.dumps({"error": str(e)}), 500, {'Content-Type': 'application/json'}