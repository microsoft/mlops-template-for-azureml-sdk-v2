variable "basename" {
  type = string
  # default = "mlopsv2"
  default = ""
}

variable "location" {
  type = string
  # default = "westus2"
  default = ""
}

variable "resource_group_name" {
  type = string
  # default = "rg-mlopsv2-aml-001"
  default = ""
}

variable "application_insights_id" {
  type = string
  # default = "ai-mlopsv2-appinsight-001"
  default = ""
}

variable "key_vault_id" {
  type = string
  # default = "kv-mlopsv2-keyvault-001"
  default = ""
}

variable "storage_account_id" {
  type = string
  # default = "sa-mlopsv2-storageaccount-001"
  default = ""
}

variable "container_registry_id" {
  type = string
  # default = "cr-mlopsv2-containerregistery-001"
  default = ""
}
