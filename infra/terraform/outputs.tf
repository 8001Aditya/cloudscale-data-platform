output "resource_group_name" {
  description = "Name of the Azure Resource Group created for this phase."
  value       = azurerm_resource_group.main.name
}

output "resource_group_location" {
  description = "Azure region of the Resource Group created for this phase."
  value       = azurerm_resource_group.main.location
}
