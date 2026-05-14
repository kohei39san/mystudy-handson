data "azurerm_subscription" "current" {}

resource "azurerm_resource_group" "main" {
  name     = var.resource_group_name
  location = var.location
  tags     = var.tags
}

resource "azurerm_monitor_action_group" "billing_alert" {
  name                = var.action_group_name
  resource_group_name = azurerm_resource_group.main.name
  short_name          = var.action_group_short_name
  tags                = var.tags

  dynamic "email_receiver" {
    for_each = var.alert_email_addresses
    content {
      name          = "email-${email_receiver.key}"
      email_address = email_receiver.value
    }
  }
}

resource "azurerm_consumption_budget_subscription" "main" {
  name            = var.budget_name
  subscription_id = data.azurerm_subscription.current.id

  amount     = var.budget_amount
  time_grain = var.time_grain

  time_period {
    start_date = "${var.start_date}T00:00:00Z"
    end_date   = "${var.end_date}T00:00:00Z"
  }

  dynamic "notification" {
    for_each = var.actual_alert_thresholds
    content {
      enabled        = true
      operator       = "GreaterThan"
      threshold      = tonumber(notification.value)
      threshold_type = "Actual"

      contact_emails = var.alert_email_addresses
      contact_groups = [azurerm_monitor_action_group.billing_alert.id]
    }
  }

  notification {
    enabled        = true
    operator       = "GreaterThan"
    threshold      = tonumber(var.forecasted_alert_threshold)
    threshold_type = "Forecasted"

    contact_emails = var.alert_email_addresses
    contact_groups = [azurerm_monitor_action_group.billing_alert.id]
  }
}
