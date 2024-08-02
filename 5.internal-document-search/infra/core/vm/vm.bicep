param name string
param location string = resourceGroup().location
param adminUsername string
@secure()
param adminPasswordOrKey string
param vmSize string = 'Standard_D2s_v3'
param nicId string
param osDiskType string = 'Standard_LRS'
param isPrivateNetworkEnabled bool

param imageReference object = {
  publisher: 'MicrosoftWindowsDesktop'
  offer: 'Windows-11'
  sku: 'win11-21h2-pro'
  version: 'latest'
}

resource virtualMachine 'Microsoft.Compute/virtualMachines@2023-09-01' = if (isPrivateNetworkEnabled) {
  name: name
  location: location
  properties: {
    hardwareProfile: {
      vmSize: vmSize
    }
    osProfile: {
      computerName: name
      adminUsername: adminUsername
      adminPassword: adminPasswordOrKey
    }
    storageProfile: {
      osDisk: {
        createOption: 'FromImage'
        managedDisk: {
          storageAccountType: osDiskType
        }
      }
      imageReference: imageReference
    }
    networkProfile: {
      networkInterfaces: [
        {
          id: nicId
        }
      ]
    }
  }
}
