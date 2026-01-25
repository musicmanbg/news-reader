import json
import functions_framework
from datetime import datetime
from collections import defaultdict
from .scraper import NewsScraper
from .configs import novinite_config

def parse_novinite_date(date_str):
    """
    Parses Novinite date format: 'January 21, 2026, Wednesday // 10:02'
    """
    if not date_str:
        return datetime.min
    try:
        cleaned_date = date_str.strip()
        return datetime.strptime(cleaned_date, "%B %d, %Y, %A // %H:%M")
    except Exception as e:
        print(f"Error parsing date '{date_str}': {e}")
        return datetime.min

@functions_framework.http
def display_news(request):
    """
    HTTP Cloud Function to scrape news and return a responsive HTML page.
    """
    try:
        # Get URL from query parameters or use default archive URL
        url = request.args.get('url', 'https://www.novinite.com/archives/2025-12-28')
        
        scraper = NewsScraper(novinite_config)
        articles = scraper.scrape(url)
        
        # Sort articles by date descending
        articles.sort(key=lambda x: parse_novinite_date(x.date), reverse=True)
        
        # Group articles by category
        categories = defaultdict(list)
        for article in articles:
            categories[article.category].append(article)
            
        category_links = ""
        for cat in sorted(categories.keys()):
            cat_id = cat.replace(" ", "-").lower().replace("/", "-")
            category_links += f'<a class="flex-sm-fill text-sm-center nav-link" href="#{cat_id}">{cat}</a>'
            
        content_html = ""
        for cat in sorted(categories.keys()):
            cat_id = cat.replace(" ", "-").lower().replace("/", "-")
            content_html += f'<h2 id="{cat_id}" class="category-header">{cat}</h2>'
            
            for article in categories[cat]:
                text_content = article.content if hasattr(article, 'content') and article.content else (article.summary if article.summary else "No content available.")
                content_html += '<div class="card article-card">'
                content_html += '  <div class="card-body">'
                content_html += f'    <h4 class="card-title"><a href="{article.url}" target="_blank" class="article-title">{article.title}</a></h4>'
                content_html += f'    <div class="article-date">{article.date if article.date else ""}</div>'
                content_html += f'    <div class="article-content">{text_content}</div>'
                content_html += '  </div>'
                content_html += '</div>'

        html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>News Reader - {{SOURCE}}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { background-color: #f8f9fa; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
        .category-header { background-color: #007bff; color: white; padding: 10px 15px; border-radius: 5px; margin-top: 30px; margin-bottom: 20px; }
        .article-card { margin-bottom: 20px; border: none; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .article-title { color: #333; text-decoration: none; font-weight: bold; }
        .article-title:hover { color: #0056b3; }
        .article-date { font-size: 0.85rem; color: #6c757d; }
        .article-content { margin-top: 15px; border-top: 1px solid #eee; padding-top: 15px; }
        .navbar { background-color: #343a40 !important; }
        .nav-pills .nav-link { color: #007bff; }
        .nav-pills .nav-link:hover { background-color: #e9ecef; }
    </style>
</head>
<body>
    <nav class="navbar navbar-dark bg-dark sticky-top">
        <div class="container">
            <a class="navbar-brand" href="#">News Reader: {{SOURCE}}</a>
        </div>
    </nav>

    <div class="container my-4">
        <nav id="navbar-categories" class="nav nav-pills flex-column flex-sm-row mb-4 p-2 bg-white rounded shadow-sm">
            {{CATEGORY_LINKS}}
        </nav>
        {{CONTENT}}
    </div>

    <footer class="bg-dark text-white text-center py-3 mt-5">
        <div class="container">
            <p>&copy; 2026 News Reader - Data from {{SOURCE}}</p>
        </div>
    </footer>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
"""
        full_html = html_template.replace("{{SOURCE}}", novinite_config.name)
        full_html = full_html.replace("{{CATEGORY_LINKS}}", category_links)
        full_html = full_html.replace("{{CONTENT}}", content_html)
        
        return full_html, 200, {'Content-Type': 'text/html; charset=utf-8'}
    except Exception as e:
        import traceback
        error_msg = f"Error: {str(e)}\n{traceback.format_exc()}"
        return f"<html><body><h1>Internal Server Error</h1><pre>{error_msg}</pre></body></html>", 500, {'Content-Type': 'text/html'}
