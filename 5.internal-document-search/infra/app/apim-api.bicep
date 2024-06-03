param name string

param useApiManagement bool

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
param audienceClientAppId string
param audienceWebAppId string
param scopeName string = 'chat'
param apiBackendUrl string = 'https://subdomain.openai.azure.com/openai'
param tenantId string = 'xxtenantidsamplexx'

// If you want to use App Service easy auth, please use 'apim-api-policy-aad.xml'
//var policy_template = loadTextContent('./apim-api-policy.xml')
var policy_template = loadTextContent('./apim-api-policy-aad.xml')

var policy_template2 = replace(policy_template ,'{origin}', corsOriginUrl)
var policy_template3 = replace(policy_template2 ,'{aud-client-app-id}', audienceClientAppId)
var policy_template4 = replace(policy_template3 ,'{aud-web-app-id}', audienceWebAppId)
var policy_template5 = replace(policy_template4 ,'{scope-name}', scopeName)
var policy_template6 = replace(policy_template5 ,'{backend-url}', apiBackendUrl)
var apiPolicyContent = replace(policy_template6 ,'{tenant-id}', tenantId)

resource apimService 'Microsoft.ApiManagement/service@2022-08-01' existing = if (useApiManagement) {
  name: name
}

resource aoaiApi 'Microsoft.ApiManagement/service/apis@2022-08-01' = if (useApiManagement) {
  name: apiName
  parent: apimService
  properties: {
    description: apiDescription
    displayName: apiDisplayName
    path: apiPath
    protocols: [ 'https' ]
    subscriptionRequired: false
    type: 'http'
    format: 'openapi'
    serviceUrl: apiBackendUrl
    value: loadTextContent('./azure_openai_api_def.json')
    
  }
}

resource apiPolicy 'Microsoft.ApiManagement/service/apis/policies@2022-08-01' = if (useApiManagement) {
  name: 'policy'
  parent: aoaiApi
  properties: {
    format: 'rawxml'
    value: apiPolicyContent
  }
}

output apiManagementEndpoint string = useApiManagement? '${apimService.properties.gatewayUrl}/${apiPath}': ''
