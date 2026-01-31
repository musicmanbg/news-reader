terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = ">= 5.0.0"
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

data "google_project" "project" {}

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

# IAM permissions for Build Service Accounts
locals {
  build_service_accounts = [
    "serviceAccount:${data.google_project.project.number}@cloudbuild.gserviceaccount.com",
    "serviceAccount:${data.google_project.project.number}-compute@developer.gserviceaccount.com"
  ]
  roles = [
    "roles/logging.logWriter",
    "roles/storage.objectViewer",
    "roles/artifactregistry.writer",
    "roles/cloudbuild.builds.builder"
  ]
}

resource "google_project_iam_member" "build_permissions" {
  for_each = { for pair in flatten([
    for sa in local.build_service_accounts : [
      for role in local.roles : { sa = sa, role = role }
    ]
  ]) : "${pair.sa}-${pair.role}" => pair }

  project = var.project_id
  role    = each.value.role
  member  = each.value.sa
  depends_on = [google_project_service.cloudbuild, google_project_service.run]
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
    entry_point = "display_news"
    source {
      storage_source {
        bucket = google_storage_bucket.source_bucket.name
        object = google_storage_bucket_object.source_archive.name
      }
    }
  }

  service_config {
    max_instance_count = 1
    available_memory   = "512M"
    timeout_seconds    = 60
    environment_variables = {
      GCP_PROJECT  = var.project_id
      ACCESS_TOKEN = var.access_token
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

# Monitoring Notification Channel (Email)
resource "google_monitoring_notification_channel" "email" {
  display_name = "Security Alert Email"
  type         = "email"
  labels = {
    email_address = var.alert_email
  }
}

# Alert Policy for specific error messages
resource "google_monitoring_alert_policy" "unauthorized_access_alert" {
  display_name = "App Error Alert - News Reader"
  combiner     = "OR"
  conditions {
    display_name = "Specific Error Count"
    condition_threshold {
      # Updated filter to use the new app_error_count metric
      filter     = "resource.type=\"cloud_run_revision\" AND metric.type=\"logging.googleapis.com/user/app_error_count\""
      duration   = "60s"
      comparison = "COMPARISON_GT"
      threshold_value = 0 # Alert even on a single occurrence
      
      aggregations {
        alignment_period   = "60s"
        per_series_aligner = "ALIGN_RATE"
      }
    }
  }

  notification_channels = [google_monitoring_notification_channel.email.name]

  # Ensure the metric exists before the policy is created
  depends_on = [google_logging_metric.unauthorized_log_metric]

  # Optional: Documentation to include in the email
  documentation {
    content = "The News Reader application has logged the specific error: 'error something went wrong'."
  }
}

# Log-based Metric to count the specific error text
resource "google_logging_metric" "unauthorized_log_metric" {
  name   = "app_error_count"
  filter = "resource.type=\"cloud_run_revision\" AND textPayload =~ \"SECURITY: Unauthorized access attempt from*\""
  
  metric_descriptor {
    metric_kind = "DELTA"
    value_type  = "INT64"
    unit        = "1"
  }
}