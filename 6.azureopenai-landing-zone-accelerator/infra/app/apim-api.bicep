param name string

@description('Resource name to uniquely identify this API within the API Management service instance')
@minLength(1)
param apiName string

@description('The Display Name of the API')
@minLength(1)
@maxLength(300)
param apiDisplayName string

@description('Description of the API. May include HTML formatting tags.')
@minLength(1)
param apiDescription string

@description('Relative URL uniquely identifying this API and all of its resource paths within the API Management service instance. It is appended to the API endpoint base URL specified during the service instance creation to form a public URL for this API.')
@minLength(1)
param apiPath string

@description('Absolute URL of the web frontend')
param corsOriginUrl string
param audienceAppId string = 'api://xxappidsamplexx'
param scopeName string = 'chat'
param apiBackendUrl string = 'https://subdomain.openai.azure.com/openai'
param tenantId string = 'xxtenantidsamplexx'

// If you want to use App Service easy auth, please use 'apim-api-policy-aad.xml'
//var policy_template = loadTextContent('./apim-api-policy.xml')
var policy_template = loadTextContent('./apim-api-policy-aad.xml')

var policy_template2 = replace(policy_template ,'{origin}', corsOriginUrl)
var policy_template3 = replace(policy_template2 ,'{aud-app-id}', audienceAppId)
var policy_template4 = replace(policy_template3 ,'{scope-name}', scopeName)
var policy_template5 = replace(policy_template4 ,'{backend-url}', apiBackendUrl)
var apiPolicyContent = replace(policy_template5 ,'{tenant-id}', tenantId)

resource apimService 'Microsoft.ApiManagement/service@2021-08-01' existing = {
  name: name
}

resource aoaiApi 'Microsoft.ApiManagement/service/apis@2021-12-01-preview' = {
  name: apiName
  parent: apimService
  properties: {
    description: apiDescription
    displayName: apiDisplayName
    path: apiPath
    protocols: [ 'https' ]
    subscriptionRequired: true
    subscriptionKeyParameterNames: {
      header: 'Ocp-Apim-Subscription-Key'
      query: 'subscription-key'
    }
    type: 'http'
    format: 'openapi'
    serviceUrl: apiBackendUrl
    value: loadTextContent('./azure_openai_api_def.json')
    
  }
}

resource apiPolicy 'Microsoft.ApiManagement/service/apis/policies@2021-12-01-preview' = {
  name: 'policy'
  parent: aoaiApi
  properties: {
    format: 'rawxml'
    value: apiPolicyContent
  }
}

output SERVICE_API_URI string = '${apimService.properties.gatewayUrl}/${apiPath}'
