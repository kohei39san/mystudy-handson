# ─────────────────────────────────────────────────────────────────────────────
# GCP リソース: VPC / Firewall Rule / VM Instance / Cloud Run Service
# ─────────────────────────────────────────────────────────────────────────────

# --- VPC Network ---

resource "google_compute_network" "main" {
  name                    = "${var.project_name}-vpc"
  auto_create_subnetworks = false
}

# --- Subnet ---

resource "google_compute_subnetwork" "main" {
  name          = "${var.project_name}-subnet"
  region        = var.gcp_region
  network       = google_compute_network.main.id
  ip_cidr_range = "10.2.0.0/24"
}

# --- Firewall Rule: 接続許可パターン（HTTP / HTTPS / SSH）---
# internet_reachability=reachable を確認するためのテスト用ルール。本番環境では使用しないこと

resource "google_compute_firewall" "allow_http_https_ssh" {
  name    = "${var.project_name}-allow-http-https-ssh"
  network = google_compute_network.main.name

  allow {
    protocol = "tcp"
    ports    = ["22", "80", "443"]
  }

  source_ranges = ["0.0.0.0/0"]
  target_tags   = ["allow-http-https-ssh"]

  description = "Allow HTTP/HTTPS/SSH from anywhere (integration test - allow pattern)"
}

# --- Firewall Rule: 接続拒否パターン（カスタムポート 8080）---

resource "google_compute_firewall" "deny_custom_port" {
  name    = "${var.project_name}-deny-custom-port"
  network = google_compute_network.main.name

  deny {
    protocol = "tcp"
    ports    = ["8080"]
  }

  source_ranges = ["0.0.0.0/0"]
  target_tags   = ["deny-custom-port"]
  priority      = 1000

  description = "Deny custom port 8080 from anywhere (integration test - deny pattern)"
}

# --- VM Instance（外部 IP あり + ファイアウォールタグ付き → internet_reachability=reachable）---

resource "google_compute_instance" "test" {
  name         = "${var.project_name}-vm"
  machine_type = var.gcp_vm_machine_type
  zone         = var.gcp_zone

  boot_disk {
    initialize_params {
      image = var.gcp_vm_image
    }
  }

  network_interface {
    network    = google_compute_network.main.id
    subnetwork = google_compute_subnetwork.main.id

    # 外部 IP を付与（internet_reachability=reachable）
    access_config {}
  }

  tags = ["allow-http-https-ssh"]

  labels = {
    project     = var.project_name
    environment = var.environment
    managed_by  = "terraform"
  }
}

# --- Cloud Run Service（ingress=all → internet_reachability=reachable）---

resource "google_cloud_run_v2_service" "test" {
  name     = "${var.project_name}-cloudrun"
  location = var.gcp_region
  ingress  = "INGRESS_TRAFFIC_ALL"

  template {
    containers {
      image = var.gcp_cloudrun_image

      ports {
        container_port = 8080
      }

      resources {
        limits = {
          cpu    = "1"
          memory = "512Mi"
        }
      }
    }
  }

  labels = {
    project     = var.project_name
    environment = var.environment
    managed_by  = "terraform"
  }
}

# --- Cloud Run: 未認証呼び出しを許可（パブリックアクセス）---

resource "google_cloud_run_v2_service_iam_member" "public_invoker" {
  project  = var.gcp_project_id
  location = var.gcp_region
  name     = google_cloud_run_v2_service.test.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}
