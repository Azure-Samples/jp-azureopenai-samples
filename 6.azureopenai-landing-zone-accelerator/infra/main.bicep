targetScope = 'subscription'

@minLength(1)
@maxLength(64)
@description('Name of the the environment which is used to generate a short unique hash used in all resources.')
param environmentName string

@minLength(1)
@description('Primary location for all resources')
param location string

param storageAccountName string = ''
param storageResourceGroupLocation string = location
param storageContainerName string = 'content'

// Optional parameters to override the default azd resource naming conventions. Update the main.parameters.json file to provide values. e.g.,:
// "resourceGroupName": {
//      "value": "myGroupName"
// }

param applicationInsightsDashboardName string = ''
param applicationInsightsName string = ''
param logAnalyticsName string = ''
param resourceGroupName string = ''
param apimServiceName string = ''

// Please provide these parameters if you want to use an existing Azure OpenAI resource
param openAiServiceName string = ''
param openAiResourceGroupName string = ''
param openAiResourceGroupLocation string = location
param aoaiCapacity int = 10

// Please provide these parameters if you need to create a new Azure OpenAI resource
param openAiSkuName string = 'S0'
param openAiGpt35TurboDeploymentName string = 'gpt-35-turbo-deploy'
param openAiGpt35Turbo16kDeploymentName string = 'gpt-35-turbo-16k-deploy'

// params for api policy settings
@description('CORSオリジンとして許可するドメインを指定してください(*でも可)')
param corsOriginUrl string = '*'
@description('認可対象となるAzure ADに登録されたアプリのIDを指定してください（例: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx）')
param audienceAppId string = 'xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx'
@description('認可対象となるをAzure ADに登録されたアプリのスコープ名を指定してください')
param scopeName string = 'chat'
@description('認証対象となるAzure ADのテナントIDを指定してください')
param tenantId string = 'xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx'

var abbrs = loadJsonContent('./abbreviations.json')
var resourceToken = toLower(uniqueString(subscription().id, environmentName, location))
var tags = { 'azd-env-name': environmentName }

// Organize resources in a resource group
resource rg 'Microsoft.Resources/resourceGroups@2021-04-01' = {
  name: !empty(resourceGroupName) ? resourceGroupName : '${abbrs.resourcesResourceGroups}${environmentName}'
  location: location
  tags: tags
}

//  Refer Azure OpenAI resource group if it is provided (if not provided, use the resource group created above)
resource openAiResourceGroup 'Microsoft.Resources/resourceGroups@2021-04-01' existing = if (!empty(openAiResourceGroupName)) {
  name: !empty(openAiResourceGroupName) ? openAiResourceGroupName : rg.name
}

module openAi 'core/ai/cognitiveservices.bicep' = {
  name: 'openai'
  scope: openAiResourceGroup
  params: {
    name: !empty(openAiServiceName) ? openAiServiceName : '${abbrs.cognitiveServicesAccounts}${resourceToken}'
    location: openAiResourceGroupLocation
    tags: tags
    sku: {
      name: openAiSkuName
      capacity: aoaiCapacity
    }
    deployments: [
      {
        name: openAiGpt35TurboDeploymentName
        model: {
          format: 'OpenAI'
          name: 'gpt-35-turbo'
          version: '0613'
        }
        sku: {
          name: 'Standard'
          capacity: 120
        }
      }
      {
        name: openAiGpt35Turbo16kDeploymentName
        model: {
          format: 'OpenAI'
          name: 'gpt-35-turbo-16k'
          version: '0613'
        }
        sku: {
          name: 'Standard'
          capacity: 120
        }
      }
    ]
  }
}

// Storage Account
module storage 'core/storage/storage-account.bicep' = {
  name: 'storage'
  scope: rg
  params: {
    name: !empty(storageAccountName) ? storageAccountName : '${abbrs.storageStorageAccounts}${resourceToken}'
    location: storageResourceGroupLocation
    tags: tags
    publicNetworkAccess: 'Enabled'
    sku: {
      name: 'Standard_ZRS'
    }
    deleteRetentionPolicy: {
      enabled: true
      days: 2
    }
    containers: [
      {
        name: storageContainerName
        publicAccess: 'None'
      }
    ]
  }
}

// Monitor application with Azure Monitor
module monitoring './core/monitor/monitoring.bicep' = {
  name: 'monitoring'
  scope: rg
  params: {
    location: location
    tags: tags
    logAnalyticsName: !empty(logAnalyticsName) ? logAnalyticsName : '${abbrs.operationalInsightsWorkspaces}${resourceToken}'
    applicationInsightsName: !empty(applicationInsightsName) ? applicationInsightsName : '${abbrs.insightsComponents}${resourceToken}'
    applicationInsightsDashboardName: !empty(applicationInsightsDashboardName) ? applicationInsightsDashboardName : '${abbrs.portalDashboards}${resourceToken}'
  }
}

// Creates Azure API Management (APIM) service to mediate the requests between the frontend and the backend API
module apim './core/gateway/apim.bicep' = {
  name: 'apim-deployment'
  scope: rg

  params: {
    name: !empty(apimServiceName) ? apimServiceName : '${abbrs.apiManagementService}${resourceToken}'
    location: location
    tags: tags
    sku: 'Standard'
    skuCount: 1
    applicationInsightsName: monitoring.outputs.applicationInsightsName
    workspaceId: monitoring.outputs.logAnalyticsWorkspaceId
    storageAccountId: storage.outputs.id
  }
}


// Assigns a role to Azure OpenAI API Management service to access Azure OpenAI
module aoaiRole 'core/security/role.bicep' = {
  scope: openAiResourceGroup
  name: 'search-role-backend'
  params: {
    principalId: apim.outputs.identityPrincipalId
    // Cognitive Services OpenAI user
    roleDefinitionId: '5e0bd9bd-7b93-4f28-af87-19fc36ad61bd'
    principalType: 'ServicePrincipal'
  }
}


// Configures the API in the Azure API Management (APIM) service
module apimApi './app/apim-api.bicep' = {
  name: 'apim-api-deployment'
  scope: rg
  dependsOn: [
    apim
  ]
  params: {
    name: apim.outputs.apimServiceName
    apiName: 'azure-openai-api'
    apiDisplayName: 'Azure OpenAI API'
    apiDescription: 'This is proxy endpoints for Azure OpenAI API'
    apiPath: 'api'

    //API Policy parameters
    corsOriginUrl: corsOriginUrl
    audienceAppId: audienceAppId
    scopeName: scopeName
    apiBackendUrl: 'https://${openAi.outputs.name}.openai.azure.com/openai'
    tenantId: tenantId
  }
}
// next action
// 1.ポリシーを簡略化する
// 2.VNet統合する

// App outputs
output APPLICATIONINSIGHTS_CONNECTION_STRING string = monitoring.outputs.applicationInsightsConnectionString
output AZURE_LOCATION string = location
output AZURE_TENANT_ID string = tenant().tenantId
output REACT_APP_APPLICATIONINSIGHTS_CONNECTION_STRING string = monitoring.outputs.applicationInsightsConnectionString
