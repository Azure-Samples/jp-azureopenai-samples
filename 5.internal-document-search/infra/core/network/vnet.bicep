param name string
param location string
param addressPrefixes array
param isPrivateNetworkEnabled bool

resource vnet 'Microsoft.Network/virtualNetworks@2023-11-01' = if (isPrivateNetworkEnabled) {
  name: name
  location: location
  properties: {
    addressSpace: {
      addressPrefixes: addressPrefixes
    }
  }
}

output id string = vnet.id
output name string = vnet.name
