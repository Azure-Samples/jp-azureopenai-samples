param name string
param cosmosDbDatabaseName string
param cosmosDbContainerName string
param location string = resourceGroup().location
param tags object = {}
@allowed(['Enabled', 'Disabled'])
param publicNetworkAccess string

resource cosmosDbAccount 'Microsoft.DocumentDB/databaseAccounts@2024-05-15' = {
  name: name
  location: location
  tags: tags
  kind: 'GlobalDocumentDB'
  properties: {
    consistencyPolicy: {
      defaultConsistencyLevel: 'Session'
    }
    databaseAccountOfferType: 'Standard'
    locations: [
      {
        locationName: location
      }]
      publicNetworkAccess: publicNetworkAccess
  }
}

resource cosmosDbDatabase 'Microsoft.DocumentDB/databaseAccounts/sqlDatabases@2021-04-15' = {
  parent: cosmosDbAccount
  name: cosmosDbDatabaseName
  properties: {
    resource: {
      id: cosmosDbDatabaseName
    }
    options: {
      throughput: 400
    }
  }

}

resource cosmosDbContainer 'Microsoft.DocumentDB/databaseAccounts/sqlDatabases/containers@2021-04-15' = {
  parent: cosmosDbDatabase
  name: cosmosDbContainerName
  properties: {
    resource: {
      id: cosmosDbContainerName
      partitionKey: {
        paths: [
          '/id'
        ]
        kind: 'Hash'
      }
    }
  }
}

output id string = cosmosDbAccount.id
output name string = cosmosDbAccount.name
output endpoint string = cosmosDbAccount.properties.documentEndpoint
output databaseName string = cosmosDbDatabase.name
output containerName string = cosmosDbContainer.name
output accountName string = cosmosDbAccount.name
