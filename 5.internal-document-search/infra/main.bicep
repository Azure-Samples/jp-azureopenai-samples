targetScope = 'subscription'

@minLength(1)
@maxLength(64)
@description('Name of the the environment which is used to generate a short unique hash used in all resources.')
param environmentName string

@minLength(1)
@description('Primary location for all resources')
param location string

@description('Enable private network access to the backend service')
param isPrivateNetworkEnabled bool

param principalType string = ''

param appServicePlanName string = ''
param backendServiceName string = ''
param resourceGroupName string = ''

param applicationInsightsName string = ''
param workspaceName string = ''

param searchServiceName string = ''
param searchServiceResourceGroupName string = ''
param searchServiceResourceGroupLocation string = location

param searchServiceSkuName string = 'standard'
param searchIndexName string = 'gptkbindex'

param storageAccountName string = ''
param storageResourceGroupName string = ''
param storageResourceGroupLocation string = location
param storageContainerName string = 'content'

param openAiServiceName string = ''
param openAiResourceGroupName string = ''

@allowed([
  '1.  australiaeast    (You can deploy GPT-4 and GPT-3 models)'
  '2.  canadaeast       (You can deploy GPT-4 and GPT-3 models)'
  '3.  swedencentral    (You can deploy GPT-4 and GPT-3 models)'
  '4.  switzerlandnorth (You can deploy GPT-4 and GPT-3 models)'
  '5.  eastus           (You can deploy only GPT-3 models)'
  '6.  eastus2          (You can deploy only GPT-3 models)'
  '7.  francecentral    (You can deploy only GPT-3 models)'
  '8.  japaneast        (You can deploy only GPT-3 models)'
  '9.  northcentralus   (You can deploy only GPT-3 models)'
  '10. uksouth          (You can deploy only GPT-3 models)'
])
param AzureOpenAIServiceRegion string

param delimiters array = ['.', '(']
param aoaiRegionWithBlankSpace string = split(AzureOpenAIServiceRegion, delimiters)[1]
param openAiResourceGroupLocation string = trim(aoaiRegionWithBlankSpace)
param useOpenAiGpt4 bool = contains(AzureOpenAIServiceRegion, 'GPT-4')

param openAiSkuName string = 'S0'
param openAiGpt35TurboDeploymentName string = 'gpt-35-turbo-deploy'
param openAiGpt35Turbo16kDeploymentName string = 'gpt-35-turbo-16k-deploy'
param openAiGpt4DeploymentName string = 'gpt-4-deploy'
param openAiGpt432kDeploymentName string = 'gpt-4-32k-deploy'
param openAiApiVersion string = '2023-05-15'

param formRecognizerServiceName string = ''
param formRecognizerResourceGroupName string = ''
param formRecognizerResourceGroupLocation string = location

param formRecognizerSkuName string = 'S0'

param cosmosDBAccountName string = ''
param cosmosDbDatabaseName string = 'ChatHistory'
param cosmosDbContainerName string = 'Prompts'

param apiManagementResourceGroupName string = ''

param vnetLocation string = location
param vnetAddressPrefix string = '10.0.0.0/16'

param subnetAddressPrefix1 string = '10.0.0.0/24'
param subnetAddressPrefix2 string = '10.0.1.0/24'
param subnetAddressPrefix3 string = '10.0.2.0/24'

param privateEndpointLocation string = location

param vmLoginName string = 'azureuser'
@secure()
param vmLoginPassword string


@description('Id of the user or app to assign application roles')
param principalId string = ''

@description('Use Application Insights for monitoring and performance tracing')
param useApplicationInsights bool = true

@description('Use API Management for protect Azure OpenAI service API endpoints')
param useApiManagement bool

param apimServiceName string = ''

// params for api policy settings
@description('Specify the domains allowed as CORS origins')
param corsOriginUrl string = '*'

@description('Provide the ID of the registered app in the Azure AD that is authorized')
param audienceClientAppId string = ''
param audienceWebAppId string = ''

@description('Specify the scope name of the registered app in Azure AD that is authorized')
param scopeName string = 'chat'

@description('Provide the Tenant ID of the Azure AD for authentication purposes')
param tenantId string = ''

var abbrs = loadJsonContent('abbreviations.json')
var resourceToken = toLower(uniqueString(subscription().id, environmentName, location))
var tags = { 'azd-env-name': environmentName }

// Organize resources in a resource group
resource resourceGroup 'Microsoft.Resources/resourceGroups@2024-03-01' = {
  name: !empty(resourceGroupName) ? resourceGroupName : '${abbrs.resourcesResourceGroups}${environmentName}'
  location: location
  tags: tags
}

resource openAiResourceGroup 'Microsoft.Resources/resourceGroups@2024-03-01' existing = if (!empty(openAiResourceGroupName)) {
  name: !empty(openAiResourceGroupName) ? openAiResourceGroupName : resourceGroup.name
}

resource formRecognizerResourceGroup 'Microsoft.Resources/resourceGroups@2024-03-01' existing = if (!empty(formRecognizerResourceGroupName)) {
  name: !empty(formRecognizerResourceGroupName) ? formRecognizerResourceGroupName : resourceGroup.name
}

resource searchServiceResourceGroup 'Microsoft.Resources/resourceGroups@2024-03-01' existing = if (!empty(searchServiceResourceGroupName)) {
  name: !empty(searchServiceResourceGroupName) ? searchServiceResourceGroupName : resourceGroup.name
}

resource storageResourceGroup 'Microsoft.Resources/resourceGroups@2024-03-01' existing = if (!empty(storageResourceGroupName)) {
  name: !empty(storageResourceGroupName) ? storageResourceGroupName : resourceGroup.name
}

resource apiManagementResourceGroup 'Microsoft.Resources/resourceGroups@2024-03-01' existing = if (!empty(apiManagementResourceGroupName)) {
  name: !empty(apiManagementResourceGroupName) ? apiManagementResourceGroupName : resourceGroup.name
}

module cosmosDb 'core/db/cosmosdb.bicep' = {
  name: 'cosmosdb'
  scope: resourceGroup
  params: {
    name: !empty(cosmosDBAccountName) ? cosmosDBAccountName : '${abbrs.documentDBDatabaseAccounts}${resourceToken}'
    location: location
    tags: union(tags, { 'azd-service-name': 'cosmosdb' })
    cosmosDbDatabaseName: cosmosDbDatabaseName
    cosmosDbContainerName: cosmosDbContainerName
    publicNetworkAccess: isPrivateNetworkEnabled ? 'Disabled' : 'Enabled'
  }
}

// Create an App Service Plan to group applications under the same payment plan and SKU
module appServicePlan 'core/host/appserviceplan.bicep' = {
  name: 'appserviceplan'
  scope: resourceGroup
  params: {
    name: !empty(appServicePlanName) ? appServicePlanName : '${abbrs.webServerFarms}${resourceToken}'
    location: location
    tags: tags
    sku: {
      name: 'S1'
      capacity: 1
    }
    kind: 'linux'
  }
}

// Monitor application with Azure Monitor
module monitoring './core/monitor/monitoring.bicep' = if (useApplicationInsights) {
  name: 'monitoring'
  scope: resourceGroup
  params: {
    workspaceName: !empty(workspaceName) ? workspaceName : '${abbrs.insightsComponents}${resourceToken}-workspace'
    location: location
    tags: tags
    applicationInsightsName: !empty(applicationInsightsName) ? applicationInsightsName : '${abbrs.insightsComponents}${resourceToken}'
  }
}

// The application frontend
module backend 'core/host/appservice.bicep' = {
  name: 'web'
  scope: resourceGroup
  params: {
    name: !empty(backendServiceName) ? backendServiceName : '${abbrs.webSitesAppService}backend-${resourceToken}'
    location: location
    tags: union(tags, { 'azd-service-name': 'backend' })
    appServicePlanId: appServicePlan.outputs.id
    runtimeName: 'python'
    runtimeVersion: '3.10'
    scmDoBuildDuringDeployment: true
    managedIdentity: true
    applicationInsightsName: useApplicationInsights ? monitoring.outputs.applicationInsightsName : ''
    virtualNetworkSubnetId: isPrivateNetworkEnabled ? appServiceSubnet.outputs.id : ''
    appSettings: {
      APPLICATIONINSIGHTS_CONNECTION_STRING: useApplicationInsights ? monitoring.outputs.applicationInsightsConnectionString : ''
      AZURE_APP_SERVICE_ENDPOINT: !empty(backendServiceName) ? backendServiceName : '${abbrs.webSitesAppService}backend-${resourceToken}'
      AZURE_STORAGE_ACCOUNT: storage.outputs.name
      AZURE_STORAGE_CONTAINER: storageContainerName
      AZURE_OPENAI_SERVICE: openAi.outputs.name
      AZURE_SEARCH_INDEX: searchIndexName
      AZURE_SEARCH_SERVICE: searchService.outputs.name
      AZURE_OPENAI_GPT_35_TURBO_DEPLOYMENT: openAiGpt35TurboDeploymentName
      AZURE_OPENAI_GPT_35_TURBO_16K_DEPLOYMENT: openAiGpt35Turbo16kDeploymentName
      AZURE_OPENAI_GPT_4_DEPLOYMENT: openAiGpt4DeploymentName
      AZURE_OPENAI_GPT_4_32K_DEPLOYMENT: openAiGpt432kDeploymentName
      AZURE_OPENAI_API_VERSION: '2023-05-15'
      AZURE_COSMOSDB_CONTAINER: cosmosDbContainerName
      AZURE_COSMOSDB_DATABASE: cosmosDbDatabaseName
      AZURE_COSMOSDB_ENDPOINT: cosmosDb.outputs.endpoint
      API_MANAGEMENT_ENDPOINT: useApiManagement ? apimApi.outputs.apiManagementEndpoint : ''
      ENTRA_CLIENT_ID: audienceClientAppId
      USE_API_MANAGEMENT: useApiManagement
    }
  }
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
    }
    useOpenAiGpt4: useOpenAiGpt4
    openAiGpt35TurboDeploymentName: openAiGpt35TurboDeploymentName
    openAiGpt35Turbo16kDeploymentName: openAiGpt35Turbo16kDeploymentName
    openAiGpt4DeploymentName: openAiGpt4DeploymentName
    openAiGpt432kDeploymentName: openAiGpt432kDeploymentName
    publicNetworkAccess: isPrivateNetworkEnabled ? 'Disabled' : 'Enabled'
  }
}

module formRecognizer 'core/ai/cognitiveservices.bicep' = {
  name: 'formrecognizer'
  scope: formRecognizerResourceGroup
  params: {
    name: !empty(formRecognizerServiceName) ? formRecognizerServiceName : '${abbrs.cognitiveServicesFormRecognizer}${resourceToken}'
    kind: 'FormRecognizer'
    location: formRecognizerResourceGroupLocation
    tags: tags
    sku: {
      name: formRecognizerSkuName
    }
    deployments: []
  }
}

module searchService 'core/search/search-services.bicep' = {
  name: 'search-service'
  scope: searchServiceResourceGroup
  params: {
    name: !empty(searchServiceName) ? searchServiceName : 'gptkb-${resourceToken}'
    location: searchServiceResourceGroupLocation
    tags: tags
    authOptions: {
      aadOrApiKey: {
        aadAuthFailureMode: 'http401WithBearerChallenge'
      }
    }
    sku: {
      name: searchServiceSkuName
    }
    semanticSearch: 'free'
  }
}

module storage 'core/storage/storage-account.bicep' = {
  name: 'storage'
  scope: storageResourceGroup
  params: {
    name: !empty(storageAccountName) ? storageAccountName : '${abbrs.storageStorageAccounts}${resourceToken}'
    location: storageResourceGroupLocation
    tags: tags
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
    publicNetworkAccess: 'Enabled'
  }
}

// ================================================================================================
// API Management
// ================================================================================================
module apim './core/gateway/apim.bicep' = {
  name: 'apim'
  scope: apiManagementResourceGroup
  params: {
    name: !empty(apimServiceName) ? apimServiceName : '${abbrs.apiManagementService}${resourceToken}'
    location: location
    tags: tags
    useApiManagement: useApiManagement
    sku: 'Standard'
    skuCount: 1
    applicationInsightsName: monitoring.outputs.applicationInsightsName
    workspaceId: monitoring.outputs.logAnalyticsWorkspaceId
    storageAccountId: storage.outputs.id
  }
}

// Configures the API in the Azure API Management (APIM) service
module apimApi './app/apim-api.bicep' = {
  name: 'apimapi'
  scope: apiManagementResourceGroup
  dependsOn: [
    apim
  ]
  params: {
    name: !empty(apimServiceName) ? apimServiceName : '${abbrs.apiManagementService}${resourceToken}'
    useApiManagement: useApiManagement
    apiName: 'azure-openai-api'
    apiDisplayName: 'Azure OpenAI API'
    apiDescription: 'This is proxy endpoints for Azure OpenAI API'
    apiPath: 'api'

    //API Policy parameters
    corsOriginUrl: corsOriginUrl
    audienceClientAppId: audienceClientAppId
    audienceWebAppId: audienceWebAppId
    scopeName: scopeName
    apiBackendUrl: 'https://${openAi.outputs.name}.openai.azure.com/openai'
    tenantId: tenantId
  }
}

// ================================================================================================
// PRIVATE NETWORK VM
// ================================================================================================
module vm 'core/vm/vm.bicep' = {
  name: 'vm${resourceToken}'
  scope: resourceGroup
  params: {
    name: 'vm${resourceToken}'
    location: location
    adminUsername: vmLoginName
    adminPasswordOrKey: vmLoginPassword
    nicId: nic.outputs.nicId
    isPrivateNetworkEnabled: isPrivateNetworkEnabled
  }
  dependsOn: [
    nic
  ]
}

// ================================================================================================
// NETWORK
// ================================================================================================
module publicIP 'core/network/pip.bicep' = {
  name: 'publicIP'
  scope: resourceGroup
  params: {
    name: 'publicIP'
    location: location
    isPrivateNetworkEnabled: isPrivateNetworkEnabled
  }
}

module nsg 'core/network/nsg.bicep' = {
  name: 'nsg'
  scope: resourceGroup
  params: {
    name: 'nsg'
    location: location
    isPrivateNetworkEnabled: isPrivateNetworkEnabled
  }
}

module nic 'core/network/nic.bicep' = {
  name: 'vm-nic'
  scope: resourceGroup
  params: {
    name: 'vm-nic'
    location: location
    subnetId: vmSubnet.outputs.id
    publicIPId: publicIP.outputs.publicIPId
    nsgId: nsg.outputs.id
    isPrivateNetworkEnabled: isPrivateNetworkEnabled
  }
  dependsOn: [
    vmSubnet
    publicIP
    nsg
  ]
}

module vnet 'core/network/vnet.bicep' = {
  name: 'vnet'
  scope: resourceGroup
  params: {
    name: 'vnet'
    location: vnetLocation
    addressPrefixes: [vnetAddressPrefix]
    isPrivateNetworkEnabled: isPrivateNetworkEnabled
  }
}

module privateEndpointSubnet 'core/network/subnet.bicep' = {
  name: '${abbrs.networkVirtualNetworksSubnets}private-endpoint-${resourceToken}'
  scope: resourceGroup
  params: {
    existVnetName: vnet.outputs.name
    name: '${abbrs.networkVirtualNetworksSubnets}private-endpoint-${resourceToken}'
    addressPrefix: subnetAddressPrefix1
    networkSecurityGroup: {
      id: nsg.outputs.id
    }
    isPrivateNetworkEnabled: isPrivateNetworkEnabled
  }
  dependsOn: [
    vnet
    nsg
  ]
}

module vmSubnet 'core/network/subnet.bicep' = {
  name: '${abbrs.networkVirtualNetworksSubnets}vm-${resourceToken}'
  scope: resourceGroup
  params: {
    existVnetName: vnet.outputs.name
    name: '${abbrs.networkVirtualNetworksSubnets}vm-${resourceToken}'
    addressPrefix: subnetAddressPrefix2
    networkSecurityGroup: {
      id: nsg.outputs.id
    }
    isPrivateNetworkEnabled: isPrivateNetworkEnabled
  }
  dependsOn: [
    vnet
    nsg
    privateEndpointSubnet
  ]
}

module appServiceSubnet 'core/network/subnet.bicep' = {
  name: '${abbrs.networkVirtualNetworksSubnets}${abbrs.webSitesAppService}${resourceToken}'
  scope: resourceGroup
  params: {
    existVnetName: vnet.outputs.name
    name: '${abbrs.networkVirtualNetworksSubnets}${abbrs.webSitesAppService}${resourceToken}'
    addressPrefix: subnetAddressPrefix3
    networkSecurityGroup: {
      id: nsg.outputs.id
    }
    delegations: [
      {
        name: 'Microsoft.Web/serverFarms'
        properties: {
          serviceName: 'Microsoft.Web/serverFarms'
        }
      }
    ]
    isPrivateNetworkEnabled: isPrivateNetworkEnabled
  }
  dependsOn: [
    vnet
    nsg
    vmSubnet
  ]
}

// ================================================================================================
// PRIVATE ENDPOINT
// ================================================================================================
module appServicePrivateEndopoint 'core/network/privateEndpoint.bicep' = {
  name: 'app-service-private-endpoint'
  scope: resourceGroup
  params: {
    location: privateEndpointLocation
    name: backend.outputs.name
    subnetId: privateEndpointSubnet.outputs.id
    privateLinkServiceId: backend.outputs.id
    privateLinkServiceGroupIds: ['sites']
    dnsZoneName: 'azurewebsites.net'
    linkVnetId: vnet.outputs.id
    isPrivateNetworkEnabled: isPrivateNetworkEnabled
  }
  dependsOn: [
    privateEndpointSubnet
  ]
}

module cosmosDBPrivateEndpoint 'core/network/privateEndpoint.bicep' = {
  name: 'cosmos-private-endpoint'
  scope: resourceGroup
  params: {
    location: privateEndpointLocation
    name: cosmosDb.outputs.name
    subnetId: privateEndpointSubnet.outputs.id
    privateLinkServiceId: cosmosDb.outputs.id
    privateLinkServiceGroupIds: ['SQL']
    dnsZoneName: 'documents.azure.com'
    linkVnetId: vnet.outputs.id
    isPrivateNetworkEnabled: isPrivateNetworkEnabled
  }
  dependsOn: [
    privateEndpointSubnet
  ]
}

module oepnaiPrivateEndopoint 'core/network/privateEndpoint.bicep' = {
  name: 'openai-service-private-endpoint'
  scope: resourceGroup
  params: {
    location: privateEndpointLocation
    name: openAi.outputs.name
    subnetId: privateEndpointSubnet.outputs.id
    privateLinkServiceId: openAi.outputs.id
    privateLinkServiceGroupIds: ['account']
    dnsZoneName: 'openai.azure.com'
    linkVnetId: vnet.outputs.id
    isPrivateNetworkEnabled: isPrivateNetworkEnabled
  }
  dependsOn: [
    privateEndpointSubnet
  ]
}

module formRecognizerPrivateEndopoint 'core/network/privateEndpoint.bicep' = {
  name: 'form-recognizer-private-endpoint'
  scope: resourceGroup
  params: {
    location: privateEndpointLocation
    name: formRecognizer.outputs.name
    subnetId: privateEndpointSubnet.outputs.id
    privateLinkServiceId: formRecognizer.outputs.id
    privateLinkServiceGroupIds: ['account']
    dnsZoneName: 'cognitiveservices.azure.com'
    linkVnetId: vnet.outputs.id
    isPrivateNetworkEnabled: isPrivateNetworkEnabled
  }
  dependsOn: [
    privateEndpointSubnet
  ]
}


module storagePrivateEndopoint 'core/network/privateEndpoint.bicep' = {
  name: 'storage-private-endpoint'
  scope: resourceGroup
  params: {
    location: privateEndpointLocation
    name: storage.outputs.name
    subnetId: privateEndpointSubnet.outputs.id
    privateLinkServiceId: storage.outputs.id
    privateLinkServiceGroupIds: ['Blob']
    dnsZoneName: 'blob.core.windows.net'
    linkVnetId: vnet.outputs.id
    isPrivateNetworkEnabled: isPrivateNetworkEnabled
  }
  dependsOn: [
    privateEndpointSubnet
  ]
}

module searchServicePrivateEndopoint 'core/network/privateEndpoint.bicep' = {
  name: 'search-service-private-endpoint'
  scope: resourceGroup
  params: {
    location: privateEndpointLocation
    name: searchService.outputs.name
    subnetId: privateEndpointSubnet.outputs.id
    privateLinkServiceId: searchService.outputs.id
    privateLinkServiceGroupIds: ['searchService']
    dnsZoneName: 'search.windows.net'
    linkVnetId: vnet.outputs.id
    isPrivateNetworkEnabled: isPrivateNetworkEnabled
  }
  dependsOn: [
    privateEndpointSubnet
  ]
}

// ================================================================================================
// USER ROLES
// ================================================================================================
module openAiRoleUser 'core/security/role.bicep' = {
  scope: openAiResourceGroup
  name: 'openai-role-user'
  params: {
    principalId: principalId
    roleDefinitionId: '5e0bd9bd-7b93-4f28-af87-19fc36ad61bd'
    principalType: !empty(principalType) ? principalType : 'User'
  }
}

module formRecognizerRoleUser 'core/security/role.bicep' = {
  scope: formRecognizerResourceGroup
  name: 'formrecognizer-role-user'
  params: {
    principalId: principalId
    roleDefinitionId: 'a97b65f3-24c7-4388-baec-2e87135dc908'
    principalType: !empty(principalType) ? principalType : 'User'
  }
}

module storageRoleUser 'core/security/role.bicep' = {
  scope: storageResourceGroup
  name: 'storage-role-user'
  params: {
    principalId: principalId
    roleDefinitionId: '2a2b9908-6ea1-4ae2-8e65-a410df84e7d1'
    principalType: !empty(principalType) ? principalType : 'User'
  }
}

module storageContribRoleUser 'core/security/role.bicep' = {
  scope: storageResourceGroup
  name: 'storage-contribrole-user'
  params: {
    principalId: principalId
    roleDefinitionId: 'ba92f5b4-2d11-453d-a403-e96b0029c9fe'
    principalType: !empty(principalType) ? principalType : 'User'
  }
}

module searchRoleUser 'core/security/role.bicep' = {
  scope: searchServiceResourceGroup
  name: 'search-role-user'
  params: {
    principalId: principalId
    roleDefinitionId: '1407120a-92aa-4202-b7e9-c0e197c71c8f'
    principalType: !empty(principalType) ? principalType : 'User'
  }
}

module searchContribRoleUser 'core/security/role.bicep' = {
  scope: searchServiceResourceGroup
  name: 'search-contrib-role-user'
  params: {
    principalId: principalId
    roleDefinitionId: '8ebe5a00-799e-43f5-93ac-243d3dce84a7'
    principalType: !empty(principalType) ? principalType : 'User'
  }
}

// ================================================================================================
// SYSTEM IDENTITIES
// ================================================================================================
module openAiRoleBackend 'core/security/role.bicep' = {
  scope: openAiResourceGroup
  name: 'openai-role-backend'
  params: {
    principalId: backend.outputs.identityPrincipalId
    roleDefinitionId: '5e0bd9bd-7b93-4f28-af87-19fc36ad61bd'
    principalType: 'ServicePrincipal'
  }
}

module openAiRoleApiManagement 'core/security/role.bicep' = if (useApiManagement) {
  scope: apiManagementResourceGroup
  name: 'openai-role-api-management'
  params: {
    principalId: apim.outputs.identityPrincipalId
    roleDefinitionId: '5e0bd9bd-7b93-4f28-af87-19fc36ad61bd'
    principalType: 'ServicePrincipal'
  }
}

module storageRoleBackend 'core/security/role.bicep' = {
  scope: storageResourceGroup
  name: 'storage-role-backend'
  params: {
    principalId: backend.outputs.identityPrincipalId
    roleDefinitionId: '2a2b9908-6ea1-4ae2-8e65-a410df84e7d1'
    principalType: 'ServicePrincipal'
  }
}

module searchRoleBackend 'core/security/role.bicep' = {
  scope: searchServiceResourceGroup
  name: 'search-role-backend'
  params: {
    principalId: backend.outputs.identityPrincipalId
    roleDefinitionId: '1407120a-92aa-4202-b7e9-c0e197c71c8f'
    principalType: 'ServicePrincipal'
  }
}

output AZURE_LOCATION string = location
output AZURE_TENANT_ID string = tenant().tenantId
output AZURE_RESOURCE_GROUP string = resourceGroup.name

output AZURE_OPENAI_SERVICE string = openAi.outputs.name
output AZURE_OPENAI_RESOURCE_GROUP string = openAiResourceGroup.name
output AZURE_OPENAI_GPT_35_TURBO_DEPLOYMENT string = openAiGpt35TurboDeploymentName
output AZURE_OPENAI_GPT_35_TURBO_16K_DEPLOYMENT string = openAiGpt35Turbo16kDeploymentName
output AZURE_OPENAI_GPT_4_DEPLOYMENT string = openAiGpt4DeploymentName
output AZURE_OPENAI_GPT_4_32K_DEPLOYMENT string = openAiGpt432kDeploymentName
output AZURE_OPENAI_API_VERSION string = openAiApiVersion
output AZURE_OPENAI_RESOURCE_GROUP_LOCATION string = openAiResourceGroupLocation
output USE_OPENAI_GPT4 bool = useOpenAiGpt4

output AZURE_FORMRECOGNIZER_SERVICE string = formRecognizer.outputs.name
output AZURE_FORMRECOGNIZER_RESOURCE_GROUP string = formRecognizerResourceGroup.name

output AZURE_SEARCH_INDEX string = searchIndexName
output AZURE_SEARCH_SERVICE string = searchService.outputs.name
output AZURE_SEARCH_SERVICE_RESOURCE_GROUP string = searchServiceResourceGroup.name

output AZURE_STORAGE_ACCOUNT string = storage.outputs.name
output AZURE_STORAGE_CONTAINER string = storageContainerName
output AZURE_STORAGE_RESOURCE_GROUP string = storageResourceGroup.name

output AZURE_COSMOSDB_ENDPOINT string = cosmosDb.outputs.endpoint
output AZURE_COSMOSDB_DATABASE string = cosmosDb.outputs.databaseName
output AZURE_COSMOSDB_CONTAINER string = cosmosDb.outputs.containerName

output AZURE_COSMOSDB_ACCOUNT string = cosmosDb.outputs.accountName
output AZURE_COSMOSDB_RESOURCE_GROUP string = resourceGroup.name

output BACKEND_IDENTITY_PRINCIPAL_ID string = backend.outputs.identityPrincipalId
output BACKEND_URI string = backend.outputs.uri
output APPLICATIONINSIGHTS_CONNECTION_STRING string = useApplicationInsights ? monitoring.outputs.applicationInsightsConnectionString : ''
output API_MANAGEMENT_ENDPOINT string =  useApiManagement ? apimApi.outputs.apiManagementEndpoint : ''
