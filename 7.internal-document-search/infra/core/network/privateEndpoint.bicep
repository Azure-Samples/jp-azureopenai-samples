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

output id string = privateEndpoint.id
output name string = privateEndpoint.name
// TODO: output private ip adress
// output ip string = privateEndpoint.properties.ipConfigurations[0].properties.privateIPAddress
