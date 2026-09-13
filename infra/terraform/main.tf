locals {
  resource_group_name = "${var.project_name}-${var.environment}-rg"

  tags = {
    project     = var.project_name
    environment = var.environment
    managed_by  = "terraform"
  }
}

resource "azurerm_resource_group" "main" {
  name     = local.resource_group_name
  location = var.location
  tags     = local.tags
}

resource "azurerm_storage_account" "datalake" {
  name                     = "cloudscaledevdata"
  resource_group_name      = azurerm_resource_group.main.name
  location                 = azurerm_resource_group.main.location
  account_kind             = "StorageV2"
  account_tier             = "Standard"
  account_replication_type = "LRS"

  is_hns_enabled = true

  min_tls_version = "TLS1_2"

  public_network_access_enabled = true
  shared_access_key_enabled     = true

  tags = local.tags
}

resource "azurerm_storage_data_lake_gen2_filesystem" "datalake" {
  name               = "datalake"
  storage_account_id = azurerm_storage_account.datalake.id
}

resource "azurerm_storage_data_lake_gen2_path" "raw" {
  path               = "raw"
  filesystem_name    = azurerm_storage_data_lake_gen2_filesystem.datalake.name
  storage_account_id = azurerm_storage_account.datalake.id
  resource           = "directory"
}

resource "azurerm_storage_data_lake_gen2_path" "bronze" {
  path               = "bronze"
  filesystem_name    = azurerm_storage_data_lake_gen2_filesystem.datalake.name
  storage_account_id = azurerm_storage_account.datalake.id
  resource           = "directory"
}

resource "azurerm_storage_data_lake_gen2_path" "silver" {
  path               = "silver"
  filesystem_name    = azurerm_storage_data_lake_gen2_filesystem.datalake.name
  storage_account_id = azurerm_storage_account.datalake.id
  resource           = "directory"
}

resource "azurerm_storage_data_lake_gen2_path" "gold" {
  path               = "gold"
  filesystem_name    = azurerm_storage_data_lake_gen2_filesystem.datalake.name
  storage_account_id = azurerm_storage_account.datalake.id
  resource           = "directory"
}

resource "azurerm_storage_data_lake_gen2_path" "checkpoints" {
  path               = "checkpoints"
  filesystem_name    = azurerm_storage_data_lake_gen2_filesystem.datalake.name
  storage_account_id = azurerm_storage_account.datalake.id
  resource           = "directory"
}