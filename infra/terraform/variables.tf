variable "project_id" {
  description = "The ID of the GCP project"
  type        = string
}

variable "region" {
  description = "The region to deploy to"
  type        = string
  default     = "us-central1"
}

variable "alert_email" {
  description = "The email address to send security alerts to"
  type        = string
  default     = "ntkonstantinov@gmail.com"
}

variable "access_token" {
  description = "The access token for the application"
  type        = string
  sensitive   = true
}
