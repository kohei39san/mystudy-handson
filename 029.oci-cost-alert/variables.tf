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
  description = "Budget amount in the currency of the tenancy"
  type        = number
  default     = 100
}

variable "budget_reset_period" {
  description = "Budget reset period (MONTHLY, QUARTERLY, ANNUALLY)"
  type        = string
  default     = "MONTHLY"
}

variable "alert_threshold_percentage" {
  description = "Percentage of budget at which to trigger alert"
  type        = number
  default     = 80
}

variable "alert_email_addresses" {
  description = "List of email addresses to receive budget alerts"
  type        = list(string)
}

variable "budget_display_name" {
  description = "Display name for the budget"
  type        = string
  default     = "Monthly Budget Alert"
}

variable "freeform_tags" {
  description = "Free-form tags to apply to resources"
  type        = map(string)
  default = {
    Environment = "production"
    Purpose     = "cost-monitoring"
  }
}