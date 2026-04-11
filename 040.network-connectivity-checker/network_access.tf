# ─────────────────────────────────────────────────────────────────────────────
# 共通ネットワークアクセス制御
# ─────────────────────────────────────────────────────────────────────────────

data "http" "caller_ip" {
  url = var.caller_ip_lookup_url

  lifecycle {
    postcondition {
      condition     = self.status_code == 200
      error_message = "グローバル IP の取得に失敗しました。caller_ip_lookup_url を確認してください。"
    }
  }
}

locals {
  caller_public_ip = chomp(trimspace(data.http.caller_ip.response_body))
  allowed_cidr     = format("%s/32", local.caller_public_ip)
}
