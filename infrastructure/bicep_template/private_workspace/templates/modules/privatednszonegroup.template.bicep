@description('name for the private dns zone group resource')
param privateDnsZoneGroupName string

resource privateDnsZoneGroup 'Microsoft.Network/privateEndpoints/privateDnsZoneGroups@2022-07-01' = {
    name: privateDnsZoneGroupName
    parent: resourceSymbolicName
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