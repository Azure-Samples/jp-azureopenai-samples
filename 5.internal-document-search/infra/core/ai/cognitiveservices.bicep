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

// モデル利用可否フラグ (main.bicep の @allowed 選択結果を引き継ぐ)
param useGlobalStandard bool = true
param useAoaiGpt41 bool = true
param useAoaiGpt52 bool = false
param openAiGpt41DeploymentName string = ''
param openAiGpt41GlobalDeploymentName string = ''
param openAiGpt52DeploymentName string = ''
param openAiGpt52GlobalDeploymentName string = ''

param openAiGpt41DeployObj object = {
  name: openAiGpt41DeploymentName
  model: {
    format: 'OpenAI'
    name: 'gpt-4.1'
    version: '2025-04-14'
  }
  sku: {
    name: 'Standard'
    capacity: 40
  }
}

param openAiGpt41GlobalDeployObj object = {
  name: openAiGpt41GlobalDeploymentName
  model: {
    format: 'OpenAI'
    name: 'gpt-4.1'
    version: '2025-04-14'
  }
  sku: {
    name: 'GlobalStandard'
    capacity: 40
  }
}

param openAiGpt52DeployObj object = {
  name: openAiGpt52DeploymentName
  model: {
    format: 'OpenAI'
    name: 'gpt-5.2'
    version: '2025-09-01'
  }
  sku: {
    name: 'Standard'
    capacity: 20
  }
}

param openAiGpt52GlobalDeployObj object = {
  name: openAiGpt52GlobalDeploymentName
  model: {
    format: 'OpenAI'
    name: 'gpt-5.2'
    version: '2025-09-01'
  }
  sku: {
    name: 'GlobalStandard'
    capacity: 20
  }
}

param deployments array = useGlobalStandard ? concat(
  useAoaiGpt41 && !empty(openAiGpt41GlobalDeployObj.name) ? [ openAiGpt41GlobalDeployObj ] : [],
  useAoaiGpt52 && !empty(openAiGpt52GlobalDeployObj.name) ? [ openAiGpt52GlobalDeployObj ] : []
) : concat(
  useAoaiGpt41 && !empty(openAiGpt41DeployObj.name) ? [ openAiGpt41DeployObj ] : [],
  useAoaiGpt52 && !empty(openAiGpt52DeployObj.name) ? [ openAiGpt52DeployObj ] : []
)

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
