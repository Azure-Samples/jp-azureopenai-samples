param name string
param location string = resourceGroup().location
param tags object = {}

param useApiManagement bool

@description('The email address of the owner of the service')
@minLength(1)
param publisherEmail string = 'noreply@microsoft.com'

@description('The name of the owner of the service')
@minLength(1)
param publisherName string = 'n/a'

@description('The pricing tier of this API Management service')
@allowed([
  'Consumption'
  'Developer'
  'Standard'
  'StandardV2'
  'Premium'
])
param sku string = 'Consumption'

@description('The instance size of this API Management service.')
@allowed([ 0, 1, 2 ])
param skuCount int = 0

@description('Azure Application Insights Name')
param applicationInsightsName string
param workspaceId string
param storageAccountId string

resource apimService 'Microsoft.ApiManagement/service@2022-08-01' = if (useApiManagement) {
  name: name
  location: location
  tags: union(tags, { 'azd-service-name': name })
  sku: {
    name: sku
    capacity: (sku == 'Consumption') ? 0 : ((sku == 'Developer') ? 1 : skuCount)
  }
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    publisherEmail: publisherEmail
    publisherName: publisherName
    // Custom properties are not supported for Consumption SKU
    customProperties: sku == 'Consumption' ? {} : {
      'Microsoft.WindowsAzure.ApiManagement.Gateway.Security.Ciphers.TLS_ECDHE_RSA_WITH_AES_256_CBC_SHA': 'false'
      'Microsoft.WindowsAzure.ApiManagement.Gateway.Security.Ciphers.TLS_ECDHE_RSA_WITH_AES_128_CBC_SHA': 'false'
      'Microsoft.WindowsAzure.ApiManagement.Gateway.Security.Ciphers.TLS_RSA_WITH_AES_128_GCM_SHA256': 'false'
      'Microsoft.WindowsAzure.ApiManagement.Gateway.Security.Ciphers.TLS_RSA_WITH_AES_256_CBC_SHA256': 'false'
      'Microsoft.WindowsAzure.ApiManagement.Gateway.Security.Ciphers.TLS_RSA_WITH_AES_128_CBC_SHA256': 'false'
      'Microsoft.WindowsAzure.ApiManagement.Gateway.Security.Ciphers.TLS_RSA_WITH_AES_256_CBC_SHA': 'false'
      'Microsoft.WindowsAzure.ApiManagement.Gateway.Security.Ciphers.TLS_RSA_WITH_AES_128_CBC_SHA': 'false'
      'Microsoft.WindowsAzure.ApiManagement.Gateway.Security.Ciphers.TripleDes168': 'false'
      'Microsoft.WindowsAzure.ApiManagement.Gateway.Security.Protocols.Tls10': 'false'
      'Microsoft.WindowsAzure.ApiManagement.Gateway.Security.Protocols.Tls11': 'false'
      'Microsoft.WindowsAzure.ApiManagement.Gateway.Security.Protocols.Ssl30': 'false'
      'Microsoft.WindowsAzure.ApiManagement.Gateway.Security.Backend.Protocols.Tls10': 'false'
      'Microsoft.WindowsAzure.ApiManagement.Gateway.Security.Backend.Protocols.Tls11': 'false'
      'Microsoft.WindowsAzure.ApiManagement.Gateway.Security.Backend.Protocols.Ssl30': 'false'
    }
  }
}

// 診断設定
resource diagnosticsSettings 'Microsoft.Insights/diagnosticSettings@2021-05-01-preview' = if (useApiManagement) {
  name: '${apimService.name}-diagnosticsSetting'
  scope: apimService
  properties: {
    workspaceId: workspaceId
    storageAccountId: storageAccountId
    logAnalyticsDestinationType: 'Dedicated'
    logs: [
      {
        categoryGroup: 'allLogs'
        enabled: true
        retentionPolicy: {
          enabled: true
          // days: 360
        }
      }
      {
        categoryGroup: 'audit'
        enabled: true
        retentionPolicy: {
          enabled: true
          // days: 360
        }
      }
    ]
    metrics: [
      {
        category: 'AllMetrics'
        enabled: true
        retentionPolicy: {
          enabled: true
          // days: 360
        }
      }
    ]
  }
}

// Azure Monitorを用いる診断設定
resource apimLogger 'Microsoft.ApiManagement/service/loggers@2022-08-01' = if (useApiManagement) {
  parent: apimService
  name: 'azuremonitor'
  properties: {
    loggerType: 'azureMonitor'
    isBuffered: true
  }
}


resource apiDiagnostics 'Microsoft.ApiManagement/service/diagnostics@2022-08-01' = if (useApiManagement) {
  name: 'azuremonitor'
  parent: apimService
  properties: {
    alwaysLog: 'allErrors'
    backend: {
      request: {
        body: {
          bytes: 1024
        }
        headers: [
          'unique_name'
        ]
      }
      response: {
        body: {
          bytes: 1024
        }
      }
    }
    frontend: {
      request: {
        body: {
          bytes: 1024
        }
      }
      response: {
        body: {
          bytes: 1024
        }
      }
    }
    logClientIp: true
    loggerId: apimLogger.id
    metrics: true
    sampling: {
      percentage: 100
      samplingType: 'fixed'
    }
    verbosity: 'verbose'
  }
}


// application insights
resource appInsightsComponents 'Microsoft.Insights/components@2020-02-02' = if (useApiManagement) {
  name: applicationInsightsName
  location: location
  kind: 'other'
  properties: {
    Application_Type: 'other'
  }
}

// Application Insightsを用いる診断設定
resource apiManagement_logger_appInsights 'Microsoft.ApiManagement/service/loggers@2022-08-01' = if (useApiManagement) {
  parent: apimService
  name: 'applicationInsights'
  properties: {
    loggerType: 'applicationInsights'
    credentials: {
      instrumentationKey: reference(appInsightsComponents.id, '2015-05-01').InstrumentationKey
    }
  }
}

resource apiManagement_diagnostics_appInsights 'Microsoft.ApiManagement/service/diagnostics@2022-08-01' = if (useApiManagement) {
  parent: apimService
  name: 'applicationinsights'
  properties: {
    alwaysLog: 'allErrors'
    loggerId: apiManagement_logger_appInsights.id
    sampling: {
      samplingType: 'fixed'
      percentage: 100
    }
  }
}

output identityPrincipalId string = useApiManagement ? apimService.identity.principalId : ''
