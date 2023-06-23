// Copyright (c) Microsoft Corporation.
// Licensed under the MIT License.

param name string
param location string = resourceGroup().location
param tags object = {}

param sku object = {
  name: 'Enterprise_E10'
  capacity: 2
}

resource redisEnterprise 'Microsoft.Cache/redisEnterprise@2021-03-01' = {
  name: name
  location: location
  tags: tags
  sku: sku
  properties: {
    minimumTlsVersion: '1.2'
  }
}

output id string = redisEnterprise.id
