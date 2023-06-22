// create azure cognitive service & use open ai service
param name string
param tags object = {}
param sku object = {}
param location string
@allowed(['Disabled', 'Enabled'])
param publicNetworkAccess string

resource cognitiveServices 'Microsoft.CognitiveServices/accounts@2022-12-01' = {
  name: name
  location: location
  tags: tags
  sku: sku
  properties: {
    publicNetworkAccess: publicNetworkAccess
    customSubDomainName: name
  }
  kind: 'OpenAI'
}

// deploy OpenAI text generating model
param modelName string
param deployVersion string
@allowed(['Standard', 'Manual'])
param scaleType string

resource cognitiveServicesDeploy 'Microsoft.CognitiveServices/accounts/deployments@2022-10-01' = {
  parent: cognitiveServices
  name: name
  properties: {
    model: {
      name: modelName
      version: deployVersion
      format: 'OpenAI'
    }
    scaleSettings: {
      scaleType: scaleType
    }
  }
}


