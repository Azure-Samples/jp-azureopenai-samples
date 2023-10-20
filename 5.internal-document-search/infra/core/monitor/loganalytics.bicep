param workspaceName string = ''
param location string = resourceGroup().location
param tags object = {}

resource logAnalyticsWorkspace 'Microsoft.OperationalInsights/workspaces@2020-03-01-preview' = {
  name: workspaceName
  location: location
  tags: tags
}


output wokspaceId string = logAnalyticsWorkspace.id
