variable "project_name" {
  description = "Short project identifier used in Azure resource names and tags."
  type        = string
  default     = "cloudscale"
}

variable "environment" {
  description = "Deployment environment name, such as dev, test, staging, or prod."
  type        = string
  default     = "dev"
}

variable "location" {
  description = "Azure region for Phase 1 resources."
  type        = string
  default     = "centralindia"
}

variable "subscription_id" {
  description = "Azure subscription ID. Prefer ARM_SUBSCRIPTION_ID for local use; do not commit real IDs."
  type        = string
  default     = null
  sensitive   = true
}
