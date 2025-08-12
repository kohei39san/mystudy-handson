# Notification Topic for Budget Alerts
resource "oci_ons_notification_topic" "budget_alert_topic" {
  compartment_id = var.compartment_id
  name           = var.notification_topic_name
  description    = "Notification topic for budget alerts"

  freeform_tags = var.freeform_tags
}

# Email Subscriptions for Budget Alerts
resource "oci_ons_subscription" "budget_alert_email_subscription" {
  count          = length(var.alert_email_addresses)
  compartment_id = var.compartment_id
  endpoint       = var.alert_email_addresses[count.index]
  protocol       = "EMAIL"
  topic_id       = oci_ons_notification_topic.budget_alert_topic.id

  freeform_tags = var.freeform_tags
}