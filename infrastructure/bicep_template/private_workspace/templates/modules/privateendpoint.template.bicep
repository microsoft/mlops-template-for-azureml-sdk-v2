@description('The location into which your Azure resources should be deployed.')
param location string

@description('name for the private endpoint resource')
param privateEndpointName string

resource privateEndpoint 'Microsoft.Network/privateEndpoints@2021-08-01' = {
    name: privateEndpointName
    location: location
    properties: {
      subnet: {
        id: resourceId('Microsoft.Network/virtualNetworks/subnets', virtualNetworkName, PrivateEndpointSubnetName)
      }
      privateLinkServiceConnections: [
        {
          name: privateEndpointName
          properties: {
            privateLinkServiceId: workspace.id
            groupIds: [
              'mlworkspace']
          }
        }
      ]
    }
  }