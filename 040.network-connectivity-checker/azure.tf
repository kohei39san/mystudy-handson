# ─────────────────────────────────────────────────────────────────────────────
# Azure リソース: VNet / NSG / VM
# ─────────────────────────────────────────────────────────────────────────────

# --- Resource Group ---

resource "azurerm_resource_group" "main" {
  name     = "${var.project_name}-rg"
  location = var.azure_location

  tags = {
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}

# --- Virtual Network ---

resource "azurerm_virtual_network" "main" {
  name                = "${var.project_name}-vnet"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  address_space       = var.azure_vnet_address_space

  tags = {
    Name = "${var.project_name}-vnet"
  }
}

# --- Subnet ---

resource "azurerm_subnet" "main" {
  name                 = "${var.project_name}-subnet"
  resource_group_name  = azurerm_resource_group.main.name
  virtual_network_name = azurerm_virtual_network.main.name
  address_prefixes     = var.azure_subnet_prefix
}

# --- Network Security Group（接続許可・拒否パターンを両方定義）---
# HTTP/HTTPS/SSH 許可ルール → internet_reachability=reachable
# 特定ポートの拒否ルール例として 8080 を明示的に Deny

resource "azurerm_network_security_group" "main" {
  name                = "${var.project_name}-nsg"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name

  # SSH 許可（接続許可パターン: internet_reachability=reachable を確認するためのテスト用ルール）
  # このルールは結合テスト専用です。本番環境では使用しないこと
  security_rule {
    name                       = "AllowSSH"
    priority                   = 100
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "22"
    source_address_prefix      = local.allowed_cidr
    destination_address_prefix = "*"
  }

  # HTTP 許可（接続許可パターン）
  security_rule {
    name                       = "AllowHTTP"
    priority                   = 110
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "80"
    source_address_prefix      = local.allowed_cidr
    destination_address_prefix = "*"
  }

  # HTTPS 許可（接続許可パターン）
  security_rule {
    name                       = "AllowHTTPS"
    priority                   = 120
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "443"
    source_address_prefix      = local.allowed_cidr
    destination_address_prefix = "*"
  }

  # カスタムポート 8080 拒否（接続拒否パターン）
  security_rule {
    name                       = "DenyCustomPort"
    priority                   = 200
    direction                  = "Inbound"
    access                     = "Deny"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "8080"
    source_address_prefix      = "*"
    destination_address_prefix = "*"
  }

  tags = {
    Name = "${var.project_name}-nsg"
  }
}

# --- NSG <-> Subnet 関連付け ---

resource "azurerm_subnet_network_security_group_association" "main" {
  subnet_id                 = azurerm_subnet.main.id
  network_security_group_id = azurerm_network_security_group.main.id
}

# --- Public IP ---

resource "azurerm_public_ip" "vm" {
  name                = "${var.project_name}-vm-pip"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  allocation_method   = "Static"
  sku                 = "Standard"

  tags = {
    Name = "${var.project_name}-vm-pip"
  }
}

# --- Network Interface ---

resource "azurerm_network_interface" "vm" {
  name                = "${var.project_name}-vm-nic"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name

  ip_configuration {
    name                          = "internal"
    subnet_id                     = azurerm_subnet.main.id
    private_ip_address_allocation = "Dynamic"
    public_ip_address_id          = azurerm_public_ip.vm.id
  }

  tags = {
    Name = "${var.project_name}-vm-nic"
  }
}

# --- Virtual Machine（パブリック IP あり → internet_reachability=reachable）---

resource "azurerm_linux_virtual_machine" "test" {
  name                            = "${var.project_name}-vm"
  location                        = azurerm_resource_group.main.location
  resource_group_name             = azurerm_resource_group.main.name
  size                            = var.azure_vm_size
  admin_username                  = var.azure_vm_admin_username
  admin_password                  = var.azure_vm_admin_password
  disable_password_authentication = false
  network_interface_ids           = [azurerm_network_interface.vm.id]

  os_disk {
    caching              = "ReadWrite"
    storage_account_type = "Standard_LRS"
  }

  source_image_reference {
    publisher = "Canonical"
    offer     = "0001-com-ubuntu-server-jammy"
    sku       = "22_04-lts-arm64"
    version   = "latest"
  }

  tags = {
    Name = "${var.project_name}-vm"
  }
}
