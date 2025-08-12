variable "region" {
  description = "OCI region"
  type        = string
  default     = "ap-osaka-1"
}

variable "compartment_id" {
  description = "OCID of the compartment where resources will be created"
  type        = string
}

variable "budget_amount" {
  description = "Budget amount in the specified currency"
  type        = number
  default     = 100
}

variable "budget_currency" {
  description = "Currency for the budget (e.g., USD, JPY)"
  type        = string
  default     = "USD"
}

variable "alert_email" {
  description = "Email address to receive budget alerts"
  type        = string
}

variable "alert_threshold_percentage" {
  description = "Percentage of budget at which to trigger alert"
  type        = number
  default     = 80
}

variable "budget_display_name" {
  description = "Display name for the budget"
  type        = string
  default     = "Monthly Budget Alert"
}

variable "notification_topic_name" {
  description = "Name for the notification topic"
  type        = string
  default     = "budget-alert-topic"
}

variable "freeform_tags" {
  description = "Freeform tags to apply to resources"
  type        = map(string)
  default = {
    Environment = "production"
    Terraform   = "true"
  }
}