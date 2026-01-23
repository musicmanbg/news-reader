variable "project_id" {
  description = "The ID of the GCP project"
  type        = string
}

variable "region" {
  description = "The region to deploy to"
  type        = string
  default     = "europe-west1"
}
