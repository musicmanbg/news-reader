# News Reader

A Python project for crawling news articles and processing them.

## Project Structure
- `src/news_reader`: Main source code.
- `infra/`: Infrastructure configuration.
  - `docker-compose.yml`: Local development with GCP emulators.
  - `terraform/`: Infrastructure as Code for GCP.

## Local Development
To run the project locally with Docker:
```bash
docker-compose -f infra/docker-compose.yml up
```

## Renaming from news-parser
The project was recently renamed from `news-parser` to `news-reader`.
Please ensure you rename your local root directory if needed.
