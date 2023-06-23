// Copyright (c) Microsoft Corporation.
// Licensed under the MIT License.

param location string = resourceGroup().location
param name string
param tags object = {}

// Reference Properties
param appServicePlanId string

// Runtime Properties
@allowed([
  'dotnet', 'dotnetcore', 'dotnet-isolated', 'node', 'python', 'java', 'powershell', 'custom'
])
param runtimeName string
param runtimeNameAndVersion string = '${runtimeName}|${runtimeVersion}'
param runtimeVersion string
param kind string = 'app,linux'

// application env variables
param AZURE_OPENAI_GPT_DEPLOYMENT string
param AZURE_OPENAI_API_VERSION string
param AZURE_OPENAI_SERVICE string
param AZURE_OPENAI_API_KEY string = ''
param AZURE_OPENAI_DALLE_API_VERSION string


resource webApp 'Microsoft.Web/sites@2020-06-01' = {
  name: name
  location: location
  kind: kind
  tags: tags
  properties: {
    serverFarmId: appServicePlanId
    siteConfig: {
      linuxFxVersion: runtimeNameAndVersion
      appSettings: [
        {
          name: 'AZURE_OPENAI_GPT_DEPLOYMENT'
          value: AZURE_OPENAI_GPT_DEPLOYMENT
        }
        {
          name: 'AZURE_OPENAI_API_VERSION'
          value: AZURE_OPENAI_API_VERSION
        }
        {
          name: 'AZURE_OPENAI_SERVICE'
          value: AZURE_OPENAI_SERVICE
        }
        {
          name: 'AZURE_OPENAI_API_KEY'
          value: AZURE_OPENAI_API_KEY
        }
        {
          name: 'AZURE_OPENAI_DALLE_API_VERSION'
          value: AZURE_OPENAI_DALLE_API_VERSION
        }
      ]
    }
  }
}
