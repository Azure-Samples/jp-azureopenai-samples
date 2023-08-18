param name string
param location string
param isPrivateNetworkEnabled bool

resource publicIP 'Microsoft.Network/publicIPAddresses@2021-02-01' = if (isPrivateNetworkEnabled) {
  name: name
  location: location
  properties: {
    publicIPAllocationMethod: 'Dynamic'
  }
}

output publicIPId string = publicIP.id
// output publicIPAddress string = publicIP.properties.ipAddress
