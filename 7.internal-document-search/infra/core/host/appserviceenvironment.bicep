param name string
param location string = resourceGroup().location

param kind string
param vnetId string
param subnet string

resource appServiceEnvironment 'Microsoft.Web/hostingEnvironments@2022-03-01' = {
  name: name
  location: location
  kind: kind
  properties: {
    virtualNetwork: {
      id: vnetId
      subnet: subnet
    }
  }
}
