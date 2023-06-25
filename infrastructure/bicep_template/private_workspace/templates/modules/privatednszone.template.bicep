@description('The location into which your Azure resources should be deployed.')
param location string

@description('name for the private dns zone resource')
param privateDnsName string

resource privateDnsZone 'Microsoft.Network/privateDnsZones@2020-06-01' = {
    name: privateDnsName
    location: location
    properties: {}
        dependsOn: [
        privateEndpoint
    ]    
  }