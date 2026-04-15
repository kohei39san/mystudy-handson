resource "google_billing_budget" "main_budget" {
  billing_account = var.billing_account_id
  display_name    = var.budget_display_name

  budget_filter {
    projects = ["projects/${var.project_id}"]
  }

  amount {
    specified_amount {
      currency_code = var.currency_code
      units         = tostring(var.budget_amount)
    }
  }

  dynamic "threshold_rules" {
    for_each = var.alert_threshold_percentages
    content {
      threshold_percent = threshold_rules.value / 100
      spend_basis       = "CURRENT_SPEND"
    }
  }

  all_updates_rule {
    monitoring_notification_channels = google_monitoring_notification_channel.email[*].id
    disable_default_iam_recipients   = false
  }
}

resource "google_monitoring_notification_channel" "email" {
  count        = length(var.alert_email_addresses)
  display_name = "${var.budget_display_name}-email-${count.index}"
  type         = "email"

  labels = {
    email_address = var.alert_email_addresses[count.index]
  }
}
