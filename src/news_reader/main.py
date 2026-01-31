import json
import functions_framework
import hashlib
import os
import tempfile
from datetime import datetime
from collections import defaultdict
from flask import send_file, make_response, request
from .scraper import NewsScraper
from .configs import novinite_config
# from .tts import KokoroTTS

# Use a temporary directory for wavs to avoid triggering dev-server reloads
WAVS_DIR = os.path.join(tempfile.gettempdir(), "news_reader_wavs")
if not os.path.exists(WAVS_DIR):
    os.makedirs(WAVS_DIR)

# Initialize TTS globally to avoid reloading the model on every request
# _tts_instance = None

# def get_tts():
#     global _tts_instance
#     if _tts_instance is None:
#         try:
#             _tts_instance = KokoroTTS()
#         except Exception as e:
#             print(f"Failed to initialize TTS: {e}")
#     return _tts_instance

def get_article_hash(title):
    return hashlib.md5(title.encode('utf-8')).hexdigest()

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
    HTTP Cloud Function to scrape news and return a responsive HTML page or handle TTS.
    """
    # Security Gate: Check for access token
    expected_token = os.environ.get('ACCESS_TOKEN', 'dev-token-only')
    provided_token = request.args.get('token') or request.cookies.get('access_token')
    
    if provided_token != expected_token:
        print(f"SECURITY: Unauthorized access attempt from {request.remote_addr}")
        return "Unauthorized: Please provide a valid token.", 401

    action = request.args.get('action')
    
    # Handle streaming of audio files
    if action == 'stream_audio':
        article_hash = request.args.get('id')
        if not article_hash:
            return "Missing article ID", 400
        
        file_path = os.path.join(WAVS_DIR, f"{article_hash}.wav")
        if os.path.exists(file_path):
            return send_file(file_path, mimetype="audio/wav")
        return "Audio not found", 404

    # Handle TTS generation/status check
    if action == 'get_audio':
        article_hash = request.args.get('id')
        text = request.form.get('text')
        
        if not article_hash:
            return json.dumps({"error": "Missing ID"}), 400
        
        file_path = os.path.join(WAVS_DIR, f"{article_hash}.wav")
        
        if os.path.exists(file_path):
            return json.dumps({"status": "ready", "url": f"?action=stream_audio&id={article_hash}"}), 200
        
        if not text:
            return json.dumps({"error": "Text required for generation"}), 400
            
        try:
            # tts = get_tts()
            if tts is None:
                return json.dumps({"error": "TTS engine failed to initialize"}), 500
            tts.generate_wav(text, file_path)
            return json.dumps({"status": "ready", "url": f"?action=stream_audio&id={article_hash}"}), 200
        except Exception as e:
            return json.dumps({"error": str(e)}), 500

    # Default action: Display news
    try:
        # Get date from query params or default to today
        selected_date_str = request.args.get('date')
        if not selected_date_str:
            selected_date_str = datetime.now().strftime("%Y-%m-%d")
        
        url = f'https://www.novinite.com/archives/{selected_date_str}'
        
        scraper = NewsScraper(novinite_config)
        articles = scraper.scrape(url)
        
        articles.sort(key=lambda x: parse_novinite_date(x.date), reverse=True)
        
        categories = defaultdict(list)
        for article in articles:
            categories[article.category].append(article)
            
        category_links = ""
        for cat in sorted(categories.keys()):
            cat_id = cat.replace(" ", "-").lower().replace("/", "-")
            category_links += f'<a class="flex-sm-fill text-sm-center nav-link" href="#{cat_id}">{cat}</a>'
            
        content_html = ""
        if not articles:
            content_html = f'<div class="alert alert-info">No articles found for {selected_date_str}.</div>'
        else:
            for cat in sorted(categories.keys()):
                cat_id = cat.replace(" ", "-").lower().replace("/", "-")
                content_html += f'<h2 id="{cat_id}" class="category-header">{cat}</h2>'
                
                for article in categories[cat]:
                    text_content = article.content if hasattr(article, 'content') and article.content else (article.summary if article.summary else "No content available.")
                    article_id = get_article_hash(article.title)
                    
                    content_html += f'''
<div class="card article-card" id="card-{article_id}">
    <div class="card-body">
        <h4 class="card-title"><a href="{article.url}" target="_blank" class="article-title">{article.title}</a></h4>
        <div class="article-date">{article.date if article.date else ""}</div>
        <div class="article-content" id="text-{article_id}">{text_content}</div>
        <div class="mt-3 tts-container" id="tts-{article_id}">
            <button class="btn btn-outline-primary btn-sm read-btn" onclick="readArticle('{article_id}')" disabled>Read Article</button>
            <div class="tts-status mt-2 small text-muted" style="display:none;">Preparing the audio for the text...</div>
            <audio controls class="mt-2 w-100" style="display:none;"></audio>
        </div>
    </div>
</div>
'''

        html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>News Reader - {{SOURCE}}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body {{ background-color: #f8f9fa; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }}
        .category-header {{ background-color: #007bff; color: white; padding: 10px 15px; border-radius: 5px; margin-top: 30px; margin-bottom: 20px; }}
        .article-card {{ margin-bottom: 20px; border: none; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .article-title {{ color: #333; text-decoration: none; font-weight: bold; }}
        .article-title:hover {{ color: #0056b3; }}
        .article-date {{ font-size: 0.85rem; color: #6c757d; }}
        .article-content {{ margin-top: 15px; border-top: 1px solid #eee; padding-top: 15px; }}
        .navbar {{ background-color: #343a40 !important; }}
        .nav-pills .nav-link {{ color: #007bff; }}
        .nav-pills .nav-link:hover {{ background-color: #e9ecef; }}
        .date-picker-container {{ background: white; padding: 15px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); margin-bottom: 20px; }}
    </style>
</head>
<body>
    <nav class="navbar navbar-dark bg-dark sticky-top">
        <div class="container">
            <a class="navbar-brand" href="/">News Reader: {{SOURCE}}</a>
        </div>
    </nav>

    <div class="container my-4">
        <div class="date-picker-container d-flex flex-wrap align-items-center justify-content-between">
            <div class="mb-2 mb-md-0">
                <span class="fw-bold">Showing news for: </span>
                <span class="text-primary">{{SELECTED_DATE}}</span>
            </div>
            <div class="d-flex align-items-center">
                <label for="date-select" class="me-2 fw-bold">Select Date:</label>
                <input type="date" id="date-select" class="form-control form-control-sm" value="{{SELECTED_DATE}}" onchange="changeDate(this.value)">
            </div>
        </div>

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
    <script>
        function changeDate(date) {
            if (date) {
                const urlParams = new URLSearchParams(window.location.search);
                const token = urlParams.get('token');
                let newUrl = '?date=' + date;
                if (token) newUrl += '&token=' + token;
                window.location.href = newUrl;
            }
        }

        async function readArticle(id) {
            const container = document.getElementById('tts-' + id);
            const btn = container.querySelector('.read-btn');
            const status = container.querySelector('.tts-status');
            const audio = container.querySelector('audio');
            const text = document.getElementById('text-' + id).innerText;

            btn.disabled = true;
            status.style.display = 'block';
            status.innerText = 'Preparing the audio for the text...';

            try {
                const urlParams = new URLSearchParams(window.location.search);
                const token = urlParams.get('token');
                const formData = new FormData();
                formData.append('text', text);

                let fetchUrl = '?action=get_audio&id=' + id;
                if (token) fetchUrl += '&token=' + token;

                const response = await fetch(fetchUrl, {
                    method: 'POST',
                    body: formData
                });
                
                const data = await response.json();
                
                if (data.status === 'ready') {
                    let audioUrl = data.url;
                    if (token) audioUrl += '&token=' + token;
                    audio.src = audioUrl;
                    audio.style.display = 'block';
                    status.style.display = 'none';
                    btn.style.display = 'none';
                    audio.play();
                } else {
                    status.innerText = 'Error: ' + (data.error || 'Unknown error');
                    btn.disabled = false;
                }
            } catch (e) {
                status.innerText = 'Error: ' + e.message;
                btn.disabled = false;
            }
        }
    </script>
</body>
</html>
"""
        full_html = html_template.replace("{{SOURCE}}", novinite_config.name)
        full_html = full_html.replace("{{CATEGORY_LINKS}}", category_links)
        full_html = full_html.replace("{{CONTENT}}", content_html)
        full_html = full_html.replace("{{SELECTED_DATE}}", selected_date_str)
        
        return full_html, 200, {'Content-Type': 'text/html; charset=utf-8'}
    except Exception as e:
        import traceback
        error_msg = f"Error: {str(e)}\n{traceback.format_exc()}"
        return f"<html><body><h1>Internal Server Error</h1><pre>{error_msg}</pre></body></html>", 500, {'Content-Type': 'text/html'}
