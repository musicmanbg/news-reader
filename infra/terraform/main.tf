terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = ">= 4.0.0"
    }
    archive = {
      source  = "hashicorp/archive"
      version = "~> 2.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

# Enable necessary APIs
resource "google_project_service" "cloudfunctions" {
  service            = "cloudfunctions.googleapis.com"
  disable_on_destroy = false
}

resource "google_project_service" "run" {
  service            = "run.googleapis.com"
  disable_on_destroy = false
}

resource "google_project_service" "artifactregistry" {
  service            = "artifactregistry.googleapis.com"
  disable_on_destroy = false
}

resource "google_project_service" "cloudbuild" {
  service            = "cloudbuild.googleapis.com"
  disable_on_destroy = false
}

# Storage bucket for source code
resource "google_storage_bucket" "source_bucket" {
  name                        = "${var.project_id}-gcf-source"
  location                    = var.region
  uniform_bucket_level_access = true
}

# Create a zip of the source code
data "archive_file" "source_zip" {
  type        = "zip"
  source_dir  = "${path.module}/../../src/news_reader"
  output_path = "${path.module}/source.zip"
  excludes    = ["__pycache__", "*.pyc"]
}

# Upload the zip to the bucket
resource "google_storage_bucket_object" "source_archive" {
  name   = "source-${data.archive_file.source_zip.output_md5}.zip"
  bucket = google_storage_bucket.source_bucket.name
  source = data.archive_file.source_zip.output_path
}

# Cloud Function 2nd Gen
resource "google_cloudfunctions2_function" "news_scraper_function" {
  name        = "news-scraper-function"
  location    = var.region
  description = "Scrapes news articles"

  build_config {
    runtime     = "python311"
    entry_point = "scrape_news_http" # We will update main.py to match this
    source {
      storage_source {
        bucket = google_storage_bucket.source_bucket.name
        object = google_storage_bucket_object.source_archive.name
      }
    }
  }

  service_config {
    max_instance_count = 1
    available_memory   = "256M"
    timeout_seconds    = 60
    environment_variables = {
      GCP_PROJECT = var.project_id
    }
  }

  depends_on = [
    google_project_service.cloudfunctions,
    google_project_service.run,
    google_project_service.artifactregistry,
    google_project_service.cloudbuild
  ]
}

# IAM entry for allUsers to invoke the function (Public URL)
resource "google_cloud_run_service_iam_member" "public_invoker" {
  location = google_cloudfunctions2_function.news_scraper_function.location
  service  = google_cloudfunctions2_function.news_scraper_function.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}

output "function_uri" {
  value = google_cloudfunctions2_function.news_scraper_function.service_config[0].uri
}