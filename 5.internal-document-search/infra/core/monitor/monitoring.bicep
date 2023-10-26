param applicationInsightsName string
param workspaceName string
param location string = resourceGroup().location
param tags object = {}

module locanalytics 'loganalytics.bicep' = {
  name: 'loganalytics'
  params: {
    workspaceName: workspaceName
    location: location
    tags: tags
  }
}

module applicationInsights 'applicationinsights.bicep' = {
  name: 'applicationinsights'
  params: {
    name: applicationInsightsName
    location: location
    tags: tags
    workspaceId: locanalytics.outputs.wokspaceId
  }
}

output applicationInsightsConnectionString string = applicationInsights.outputs.connectionString
output applicationInsightsInstrumentationKey string = applicationInsights.outputs.instrumentationKey
output applicationInsightsName string = applicationInsights.outputs.name

