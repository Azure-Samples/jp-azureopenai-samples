// Copyright (c) Microsoft Corporation.
// Licensed under the MIT license.
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

resource redisEnterpriseDatabase 'Microsoft.Cache/redisEnterprise/databases@2022-11-01-preview' = {
  parent: redisEnterprise
  name: 'default'
  properties: {
    clientProtocol: 'Encrypted'
    modules: [
      {
        name: 'RediSearch'
      }
    ]
    evictionPolicy: 'AllKeysLRU'
    clusteringPolicy: 'EnterpriseCluster'
    persistence: {
      aofEnabled: false
      rdbEnabled: false
    }
  }
}

output id string = redisEnterprise.id
