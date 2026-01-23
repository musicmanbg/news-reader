provider "google" {
  project = var.project_id
  region  = var.region
}

resource "google_pubsub_topic" "articles_topic" {
  name = "articles-topic"
}

resource "google_storage_bucket" "state_bucket" {
  name     = "${var.project_id}-state-bucket"
  location = var.region
}

resource "google_cloudfunctions_function" "crawl_news" {
  name        = "crawl-news"
  description = "Crawl news and publish to Pub/Sub"
  runtime     = "python311"

  available_memory_mb   = 256
  source_archive_bucket = google_storage_bucket.state_bucket.name
  source_archive_object = "source.zip"
  trigger_http          = true
  entry_point           = "crawl_news"

  environment_variables = {
    GCP_PROJECT       = var.project_id
    STATE_BUCKET_NAME = google_storage_bucket.state_bucket.name
  }
}
