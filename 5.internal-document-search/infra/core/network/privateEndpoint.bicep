param location string = resourceGroup().location
param dnsZoneName string
param linkVnetId string
param name string
param subnetId string
param privateLinkServiceId string
param privateLinkServiceGroupIds array
param isPrivateNetworkEnabled bool

resource privateDnsZone 'Microsoft.Network/privateDnsZones@2020-06-01' = if (isPrivateNetworkEnabled) {
  name: 'privatelink.${dnsZoneName}'
  location: 'global'
}

resource virtualNetworkLinks 'Microsoft.Network/privateDnsZones/virtualNetworkLinks@2020-06-01' = if (isPrivateNetworkEnabled) {
  name: 'vnet-link-${name}'
  location: 'global'
  parent: privateDnsZone
  properties: {
    registrationEnabled: false
    virtualNetwork: {
      id: linkVnetId
    }
  }
}

// https://github.com/MicrosoftDocs/azure-docs/blob/main/articles/private-link/private-endpoint-overview.md
resource privateEndpoint 'Microsoft.Network/privateEndpoints@2023-11-01' = if (isPrivateNetworkEnabled) {
  name: '${name}-endpoint'
  location: location
  properties: {
    subnet: {
      id: subnetId
    }
    privateLinkServiceConnections: [
      {
        name: '${name}-connection}'
        properties: {
          privateLinkServiceId: privateLinkServiceId
          groupIds: privateLinkServiceGroupIds
        }
      }
    ]
  }
}

resource privateDnsZoneGroup 'Microsoft.Network/privateEndpoints/privateDnsZoneGroups@2023-11-01' = if (isPrivateNetworkEnabled) {
  parent: privateEndpoint
  name: privateDnsZone.name
  properties: {
    privateDnsZoneConfigs: [
      {
        name: 'private-link-${name}'
        properties: {
          privateDnsZoneId: privateDnsZone.id
        }
      }
    ]
  }
}

output privateEndpointId string = privateEndpoint.id
output privateEndpointName string = privateEndpoint.name
