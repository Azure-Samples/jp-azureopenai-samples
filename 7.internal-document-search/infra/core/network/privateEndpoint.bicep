param location string = resourceGroup().location
param subnetId string
param privateLinkServiceId string
param name string
param privateLinkServiceGroupIds array

resource privateEndpoint 'Microsoft.Network/privateEndpoints@2023-02-01' = {
  name: name
  location: location
  properties: {
    subnet: {
      id: subnetId
    }
    privateLinkServiceConnections: [
      {
        name: '${name}Connection}'
        properties: {
          privateLinkServiceId: privateLinkServiceId
          groupIds: privateLinkServiceGroupIds
        }
      }
    ]
  }
}

output privateEndpointId string = privateEndpoint.id
output privateEndpointName string = privateEndpoint.name
