param name string
param location string = resourceGroup().location
param subnetId string
param publicIPId string
param nsgId string

resource networkInterface 'Microsoft.Network/networkInterfaces@2021-02-01' = {
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

output nicId string = networkInterface.id
output privateIPAddress string = networkInterface.properties.ipConfigurations[0].properties.privateIPAddress
