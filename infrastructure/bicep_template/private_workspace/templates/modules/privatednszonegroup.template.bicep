@description('name for the private dns zone group resource')
param privateDnsZoneGroupName string

@description('name for the private endpoint resource')
param privateEndpointName string

@description('name for the private dns zone resource')
param privateDnsZoneName string

resource privateEndpoint 'Microsoft.Network/privateEndpoints@2021-08-01' existing = {
    name: privateEndpointName
  }
  
  resource privateDnsZone 'Microsoft.Network/privateEndpoints@2021-08-01' existing = {
    name: privateDnsZoneName
  }


resource privateDnsZoneGroup 'Microsoft.Network/privateEndpoints/privateDnsZoneGroups@2022-07-01' = {
    name: privateDnsZoneGroupName
    parent: privateEndpoint
    properties: {
      privateDnsZoneConfigs: [
        {
          name: 'config1'
          properties: {
            privateDnsZoneId: privateDnsZone.id
          }
        }
      ]
    }
    dependsOn: [
      privateEndpoint
    ]
  }