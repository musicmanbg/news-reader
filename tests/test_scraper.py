import pytest
import requests_mock
from src.news_reader.scraper import NewsScraper, ScraperConfig, Article

@pytest.fixture
def mock_config():
    return ScraperConfig(
        name="TestSite",
        base_url="https://test.com",
        item_selector="div.article",
        title_selector="h1.title",
        link_selector="a.link",
        summary_selector="p.summary",
        category_selector="span.cat"
    )

@pytest.fixture
def mock_html():
    return """
    <html>
        <body>
            <div class="article">
                <h1 class="title">Article 1</h1>
                <a class="link" href="/art1">Link 1</a>
                <p class="summary">Summary 1</p>
                <span class="cat">News</span>
            </div>
            <div class="article">
                <h1 class="title">Article 2</h1>
                <a class="link" href="https://other.com/art2">Link 2</a>
                <p class="summary">Summary 2</p>
                <span class="cat">Finance</span>
            </div>
        </body>
    </html>
    """

def test_scrape_success(mock_config, mock_html):
    url = "https://test.com/archive"
    scraper = NewsScraper(mock_config)
    
    with requests_mock.Mocker() as m:
        m.get(url, text=mock_html)
        articles = scraper.scrape(url)
        
    assert len(articles) == 2
    
    # Check first article (relative link)
    assert articles[0].title == "Article 1"
    assert articles[0].url == "https://test.com/art1"
    assert articles[0].summary == "Summary 1"
    assert articles[0].category == "News"
    assert articles[0].source == "TestSite"
    
    # Check second article (absolute link)
    assert articles[1].title == "Article 2"
    assert articles[1].url == "https://other.com/art2"
    assert articles[1].summary == "Summary 2"
    assert articles[1].category == "Finance"

def test_scrape_partial_missing_data(mock_config):
    # Missing title in one article
    html = """
    <div class="article">
        <a class="link" href="/art1">Link 1</a>
    </div>
    <div class="article">
        <h1 class="title">Article 2</h1>
        <a class="link" href="/art2">Link 2</a>
    </div>
    """
    url = "https://test.com/archive"
    scraper = NewsScraper(mock_config)
    
    with requests_mock.Mocker() as m:
        m.get(url, text=html)
        articles = scraper.scrape(url)
        
    # Should only have one valid article
    assert len(articles) == 1
    assert articles[0].title == "Article 2"

def test_scrape_no_items(mock_config):
    html = "<html><body><div class='nothing'></div></body></html>"
    url = "https://test.com/archive"
    scraper = NewsScraper(mock_config)
    
    with requests_mock.Mocker() as m:
        m.get(url, text=html)
        articles = scraper.scrape(url)
        
    assert len(articles) == 0
