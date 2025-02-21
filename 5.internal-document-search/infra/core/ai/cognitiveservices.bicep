param name string
param location string = resourceGroup().location
param tags object = {}

param customSubDomainName string = name
param kind string = 'OpenAI'
@allowed(['Enabled', 'Disabled'])
param publicNetworkAccess string = 'Enabled'
param sku object = {
  name: 'S0'
}

param useOpenAiGpt4 bool = true
param openAiGpt35TurboDeploymentName string = ''
param openAiGpt4DeploymentName string = ''
param openAiGpt4oDeploymentName string = ''

param openAiGpt35TurboDeployObj object = {
  name: openAiGpt35TurboDeploymentName
  model: {
    format: 'OpenAI'
    name: 'gpt-35-turbo'
    version: '0125'
  }
  sku: {
    name: 'Standard'
    capacity: 120
  }
}

param openAiGpt4DeployObj object = {
  name: openAiGpt4DeploymentName
  model: {
    format: 'OpenAI'
    name: 'gpt-4'
    version: 'turbo-2024-04-09'
  }
  sku: {
    name: 'Standard'
    capacity: 40
  }
}

param openAiGpt4oDeployObj object = {
  name: openAiGpt4oDeploymentName
  model: {
    format: 'OpenAI'
    name: 'gpt-4o'
    version: '2024-11-20'
  }
  sku: {
    name: 'Standard'
    capacity: 40
  }
}

param deployments array = useOpenAiGpt4? [
  openAiGpt35TurboDeployObj
  openAiGpt4DeployObj
  openAiGpt4oDeployObj
]: [
  openAiGpt35TurboDeployObj
]

resource account 'Microsoft.CognitiveServices/accounts@2023-05-01' = {
  name: name
  location: location
  tags: tags
  kind: kind
  properties: {
    customSubDomainName: customSubDomainName
    publicNetworkAccess: publicNetworkAccess
    networkAcls: {
      defaultAction: 'Allow'
    }
  }
  sku: sku
}

@batchSize(1)
resource deployment 'Microsoft.CognitiveServices/accounts/deployments@2023-05-01' = [for deployment in deployments: {
  parent: account
  name: deployment.name
  properties: {
    model: deployment.model
    raiPolicyName: contains(deployment, 'raiPolicyName') ? deployment.raiPolicyName : null
  }
  sku: contains(deployment, 'sku') ? deployment.sku : {
    name: 'Standard'
    capacity: 20
  }
}]

output endpoint string = account.properties.endpoint
output id string = account.id
output name string = account.name
