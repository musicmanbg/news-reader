import time
import os
from src.news_reader.scraper import NewsScraper
from src.news_reader.configs import novinite_config
from src.news_reader.tts import KokoroTTS

def main():
    # 1. Scrape articles
    print("Scraping articles from Novinite...")
    url = "https://www.novinite.com/archives/2025-12-28"
    scraper = NewsScraper(novinite_config)
    articles = scraper.scrape(url)
    
    if not articles:
        print("No articles found.")
        return
    
    first_article = articles[0]
    print(f"\nFirst article found:")
    print(f"Title: {first_article.title}")
    
    # We'll use title + summary for the speech
    text_to_speak = f"{first_article.title}. {first_article.summary or ''}"
    print(f"Text to generate speech for: {text_to_speak}")
    
    # 2. Generate TTS
    print("\nInitializing Kokoro TTS...")
    try:
        tts = KokoroTTS()
        output_file = "first_article.wav"
        
        print(f"Generating audio to {output_file}...")
        generation_time = tts.generate_wav(text_to_speak, output_file)
        
        print(f"\nSuccess!")
        print(f"Audio saved to: {os.path.abspath(output_file)}")
        print(f"Time taken to generate: {generation_time:.2f} seconds")
        
    except Exception as e:
        print(f"Error during TTS generation: {e}")

if __name__ == "__main__":
    main()
