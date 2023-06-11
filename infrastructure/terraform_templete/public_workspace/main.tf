data "http" "ip" {
  url = "https://ifconfig.me"
}

resource "azurerm_machine_learning_workspace" "adl_mlw" {
  name                          = "mlw-${var.basename}"
  location                      = var.location
  resource_group_name           = var.resource_group_name
  application_insights_id       = var.application_insights_id
  key_vault_id                  = var.key_vault_id
  storage_account_id            = var.storage_account_id
  container_registry_id         = var.container_registry_id
  public_network_access_enabled = true
  # image_build_compute_name      = var.image_build_compute_name
  identity {
    type = "SystemAssigned"
  }

}