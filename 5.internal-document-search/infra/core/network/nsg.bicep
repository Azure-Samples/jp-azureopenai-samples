param name string
param location string
param isPrivateNetworkEnabled bool

resource nsg 'Microsoft.Network/networkSecurityGroups@2023-11-01' = if (isPrivateNetworkEnabled) {
  name: name
  location: location
  properties: {
    securityRules: [
      {
        name: 'default-allow-3389'
        properties: {
          priority: 1000
          access: 'Allow'
          direction: 'Inbound'
          destinationPortRange: '3389'
          protocol: 'Tcp'
          sourcePortRange: '*'
          sourceAddressPrefix: '*'
          destinationAddressPrefix: '*'
        }
      }
    ]
  }
}

output id string = nsg.id
