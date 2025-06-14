param name string
param location string
param isPrivateNetworkEnabled bool

resource publicIP 'Microsoft.Network/publicIPAddresses@2023-11-01' = if (isPrivateNetworkEnabled) {
  name: name
  location: location
  sku: {
    name: 'Standard'
    tier: 'Regional'
  }
  properties: {
    publicIPAllocationMethod: 'Static'
  }
}

output publicIPId string = publicIP.id
// output publicIPAddress string = publicIP.properties.ipAddress
