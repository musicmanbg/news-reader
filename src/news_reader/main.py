import os
from datetime import datetime
from collections import defaultdict

import functions_framework
from flask import Flask, render_template_string

from .scraper import NewsScraper
from .configs import novinite_config

# HTML Template with Bootstrap 5 and Material Design principles
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>News Reader - {{ source }}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap" rel="stylesheet">
    <style>
        body {
            font-family: 'Roboto', sans-serif;
            background-color: #f8f9fa;
            color: #212529;
        }
        .navbar {
            background-color: #6200ee; /* Material Purple */
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .navbar-brand {
            font-weight: 700;
            color: white !important;
        }
        .category-header {
            border-bottom: 2px solid #6200ee;
            margin-bottom: 1.5rem;
            padding-bottom: 0.5rem;
            color: #6200ee;
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        .article-card {
            border: none;
            border-radius: 8px;
            transition: transform 0.2s, box-shadow 0.2s;
            margin-bottom: 1.5rem;
            background: white;
            box-shadow: 0 1px 3px rgba(0,0,0,0.12), 0 1px 2px rgba(0,0,0,0.24);
        }
        .article-card:hover {
            transform: translateY(-4px);
            box-shadow: 0 10px 20px rgba(0,0,0,0.19), 0 6px 6px rgba(0,0,0,0.23);
        }
        .article-title {
            font-weight: 500;
            color: #212529;
            text-decoration: none;
        }
        .article-title:hover {
            color: #6200ee;
        }
        .article-summary {
            font-size: 0.95rem;
            color: #6c757d;
        }
        .article-date {
            font-size: 0.8rem;
            color: #adb5bd;
        }
        .badge-category {
            background-color: #e0e0e0;
            color: #424242;
            font-weight: 400;
        }
        @media (max-width: 768px) {
            .container {
                padding: 10px;
            }
        }
    </style>
</head>
<body>
    <nav class="navbar navbar-dark sticky-top mb-4">
        <div class="container">
            <span class="navbar-brand">News Reader: {{ source }}</span>
            <span class="text-white-50 small">Archive: {{ archive_date }}</span>
        </div>
    </nav>

    <div class="container">
        {% for category, articles in categories.items() %}
            <section class="mb-5">
                <h2 class="category-header">{{ category }}</h2>
                <div class="row">
                    {% for article in articles %}
                        <div class="col-md-6 col-lg-4">
                            <div class="card article-card h-100">
                                <div class="card-body d-flex flex-column">
                                    <h5 class="card-title">
                                        <a href="{{ article.url }}" target="_blank" class="article-title">{{ article.title }}</a>
                                    </h5>
                                    <p class="article-summary flex-grow-1">{{ article.summary }}</p>
                                    <div class="mt-auto">
                                        <hr class="my-2">
                                        <div class="d-flex justify-content-between align-items-center">
                                            <span class="article-date">{{ article.date }}</span>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    {% endfor %}
                </div>
            </section>
        {% endfor %}
    </div>

    <footer class="bg-white py-4 mt-5 border-top">
        <div class="container text-center">
            <p class="text-muted mb-0">Powered by Gemini CLI & Novinite Scraper</p>
        </div>
    </footer>
</body>
</html>
"""

@functions_framework.http
def display_news(request):
    """
    HTTP Cloud Function that scrapes Novinite and returns a responsive web page.
    """
    # For now, we use a static archive URL as requested
    archive_date = "2025-12-28"
    url = f"https://www.novinite.com/archives/{archive_date}"
    
    print(f"Fetching news from {url}...")
    
    try:
        scraper = NewsScraper(novinite_config)
        articles = scraper.scrape(url)
        
        # Group articles by category
        grouped_articles = defaultdict(list)
        for article in articles:
            cat = article.category or "General"
            grouped_articles[cat].append(article)
            
        # Sorting within categories (they are likely already sorted by time from scraper)
        # but we ensure consistency if needed.
        
        return render_template_string(
            HTML_TEMPLATE,
            news_source=novinite_config.name,
            archive_date=archive_date,
            categories=dict(grouped_articles)
        )
        
    except Exception as e:
        print(f"Error during scraping: {e}")
        return f"<h1>Error</h1><p>Failed to load news: {str(e)}</p>", 500