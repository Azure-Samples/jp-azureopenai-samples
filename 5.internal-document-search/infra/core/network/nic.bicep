param name string
param location string
param subnetId string
param publicIPId string
param nsgId string
param isPrivateNetworkEnabled bool

resource networkInterface 'Microsoft.Network/networkInterfaces@2021-02-01' = if (isPrivateNetworkEnabled) {
  name: name
  location: location
  properties: {
    networkSecurityGroup: {
      id: nsgId
    }
    ipConfigurations: [
      {
        name: 'ipconfig'
        properties: {
          subnet: {
            id: subnetId
          }
          privateIPAllocationMethod: 'Dynamic'
          publicIPAddress: {
            id: publicIPId
          }
        }
      }
    ]
  }
}

output nicId string = networkInterface.?id
