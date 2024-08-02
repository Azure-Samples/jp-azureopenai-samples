param existVnetName string
param name string
param addressPrefix string
param networkSecurityGroup object = {}
param delegations array = []
param isPrivateNetworkEnabled bool

resource existVnet 'Microsoft.Network/virtualNetworks@2023-11-01' existing = if (isPrivateNetworkEnabled) {
  scope: resourceGroup()
  name: existVnetName
}

resource subnet 'Microsoft.Network/virtualNetworks/subnets@2023-11-01' = if (isPrivateNetworkEnabled) {
  parent: existVnet
  name: name
  properties: {
    addressPrefix: addressPrefix
    networkSecurityGroup: networkSecurityGroup
    delegations: delegations
  }
}

output id string = subnet.id
output name string = subnet.name
