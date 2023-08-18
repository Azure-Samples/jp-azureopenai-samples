param name string
param location string = resourceGroup().location

resource publicIP 'Microsoft.Network/publicIPAddresses@2021-02-01' = {
  name: name
  location: location
  properties: {
    publicIPAllocationMethod: 'Dynamic'
  }
}

output publicIPId string = publicIP.id
// output publicIPAddress string = publicIP.properties.ipAddress
