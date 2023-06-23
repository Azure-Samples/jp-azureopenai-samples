// Copyright (c) Microsoft Corporation.
// Licensed under the MIT License.

param name string
param location string = resourceGroup().location
param tenantId string = subscription().tenantId
param objectId string = ''

resource keyVault 'Microsoft.KeyVault/vaults@2022-11-01' = if(objectId != '') {
  name: name
  location: location
  properties: {
    sku: {
      family: 'A'
      name: 'standard'
    }
    tenantId: tenantId
    accessPolicies: [
      {
        tenantId: tenantId
        objectId: objectId
        permissions: {
          keys: [
            'list'
            'get'
          ]
          secrets: [
            'list'
            'get'
          ]
        }
      }
    ]
  }
}
