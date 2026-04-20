variable "project_id" {
  description = "Google Cloud project ID"
  type        = string
}

variable "region" {
  description = "Google Cloud region"
  type        = string
  default     = "asia-northeast1"
}

variable "billing_account_id" {
  description = "Google Cloud billing account ID"
  type        = string
}

variable "budget_amount" {
  description = "Budget amount in the specified currency"
  type        = number
  default     = 1
}

variable "currency_code" {
  description = "Currency code for the budget (e.g., USD, JPY)"
  type        = string
  default     = "JPY"
}

variable "budget_display_name" {
  description = "Display name for the budget"
  type        = string
  default     = "Monthly-Billing-Alert"
}

variable "alert_threshold_percentages" {
  description = "List of percentages of budget at which to trigger alerts (e.g., [50, 80, 100])"
  type        = list(number)
  default     = [50, 80, 100]
}

variable "alert_email_addresses" {
  description = "List of email addresses to receive budget alerts"
  type        = list(string)
}
