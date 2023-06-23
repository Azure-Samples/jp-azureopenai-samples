// Copyright (c) Microsoft Corporation.
// Licensed under the MIT License.

targetScope = 'subscription'

// ===================== params =====================
// resource group params
param resourceGroupName string
param resourceGroupLocation string

// openAI params
param openAIName string
@allowed(['eastus', 'westeurope', 'francecentral'])
param openAILocation string
param openAISkuName string
@allowed(['Disabled', 'Enabled'])
param openAIPublicNetworkAccess string = 'Enabled'

// openAI deploy params
param openAIDeployVersion string = '1'
@allowed(['Standard', 'Manual'])
param openAIDeployScaleType string = 'Standard'
param openAIDeployModelName string = 'text-davinci-003'

// app service plan params
param appServicePlanName string
param appServicePlanSkuName string

// app service params
param appServiceName string
param appServiceRuntimeName string = 'python'
param appServiceRuntimeVersion string = '3.10'
param AZURE_OPENAI_API_VERSION string = '2022-12-01'
param AZURE_OPENAI_DALLE_API_VERSION string = '2023-06-01-preview'

// key vault params
// @minLength(3)
// @maxLength(24)
// param keyVaultName string
// param keyVaultObjectId string

// ===================== deployment =====================

// deploy resource group
resource resourceGroup 'Microsoft.Resources/resourceGroups@2021-04-01' = {
  name: resourceGroupName
  location: resourceGroupLocation
}

module openAI 'core/ai/cognitiveServices.bicep' = {
  name: openAIName
  scope: resourceGroup
  params: {
    name: openAIName
    location: openAILocation
    tags: {}
    publicNetworkAccess: openAIPublicNetworkAccess
    sku: {
      name: openAISkuName
    }
    deployVersion: openAIDeployVersion
    modelName: openAIDeployModelName
    scaleType: openAIDeployScaleType
  }
}

// Create an App Service Plan to group applications under the same payment plan and SKU
module appServicePlan 'core/host/appServicePlan.bicep' = {
  name: appServicePlanName
  scope: resourceGroup
  params: {
    name: appServicePlanName
    location: resourceGroupLocation
    tags: {}
    sku: appServicePlanSkuName
    kind: 'linux'
  }
}

// create application deployment environment
module backend 'core/host/appService.bicep' = {
  name: appServiceName
  scope: resourceGroup
  params: {
    name: appServiceName
    location: resourceGroupLocation
    tags: {}
    appServicePlanId: appServicePlan.outputs.id
    runtimeName: appServiceRuntimeName
    runtimeVersion: appServiceRuntimeVersion
    AZURE_OPENAI_GPT_DEPLOYMENT: openAIName
    AZURE_OPENAI_API_VERSION: AZURE_OPENAI_API_VERSION
    AZURE_OPENAI_SERVICE: openAIName
    AZURE_OPENAI_DALLE_API_VERSION: AZURE_OPENAI_DALLE_API_VERSION
  }
}

// key vault for cognitive services
// module keyVault 'core/security/keyVault.bicep' = {
//   name: keyVaultName
//   scope: resourceGroup
//   params: {
//     name: keyVaultName
//     location: resourceGroupLocation
//     tenantId: subscription().tenantId
//     objectId: keyVaultObjectId
//   }
// }
