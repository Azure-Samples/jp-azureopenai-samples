param name string
param location string = resourceGroup().location
param addressPrefixes array

resource vnet 'Microsoft.Network/virtualNetworks@2023-02-01' = {
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
