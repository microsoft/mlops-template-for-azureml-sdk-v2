@description('The location into which your Azure resources should be deployed.')
param location string

@description('name for the private dns zone resource')
param privateDnsZoneName string

@description('Name of the private endpoint resource.')
param privateEndpoint string

resource pe 'Microsoft.Network/privateEndpoints@2021-08-01' existing = {
    name: privateEndpoint
  }

resource privateDnsZone 'Microsoft.Network/privateDnsZones@2020-06-01' = {
    name: privateDnsZoneName
    location: location
    properties: {}
        dependsOn: [
        pe
    ]    
  }