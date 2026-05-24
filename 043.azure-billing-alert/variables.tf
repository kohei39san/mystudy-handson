variable "subscription_id" {
  description = "Azure subscription ID"
  type        = string
}

variable "resource_group_name" {
  description = "Name of the resource group for the Action Group"
  type        = string
  default     = "rg-billing-alert"
}

variable "location" {
  description = "Azure region for the resource group"
  type        = string
  default     = "japaneast"
}

variable "budget_name" {
  description = "Name of the budget"
  type        = string
  default     = "Monthly-Billing-Alert"
}

variable "budget_amount" {
  description = "Budget amount in the subscription currency"
  type        = number
  default     = 100
}

variable "time_grain" {
  description = "Time period covered by the budget (Monthly, Quarterly, or Annual)"
  type        = string
  default     = "Monthly"

  validation {
    condition     = contains(["Monthly", "Quarterly", "Annual"], var.time_grain)
    error_message = "time_grain must be one of: Monthly, Quarterly, Annual."
  }
}

variable "start_date" {
  description = "Start date of the budget in YYYY-MM-01 format (must be the first day of the month)"
  type        = string
}

variable "end_date" {
  description = "End date of the budget in YYYY-MM-DD format"
  type        = string
}

variable "alert_email_addresses" {
  description = "List of email addresses to receive budget alert notifications"
  type        = list(string)
}

variable "actual_alert_thresholds" {
  description = "List of actual cost alert thresholds as percentages of the budget amount"
  type        = list(number)
  default     = [50, 80, 100]
}

variable "forecasted_alert_threshold" {
  description = "Forecasted cost alert threshold as a percentage of the budget amount"
  type        = number
  default     = 100
}

variable "action_group_name" {
  description = "Name of the Action Group for budget alerts"
  type        = string
  default     = "ag-billing-alert"
}

variable "action_group_short_name" {
  description = "Short name of the Action Group (max 12 characters)"
  type        = string
  default     = "BillAlert"
}

variable "tags" {
  description = "Tags to apply to resources"
  type        = map(string)
  default = {
    Terraform   = "true"
    Environment = "production"
    Purpose     = "cost-monitoring"
  }
}
