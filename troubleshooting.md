# トラブルシューティングガイド (Troubleshooting Guide)
## InsufficientQuota
### エラーメッセージ例 (Example error message)
```
{"code": "InsufficientQuota", "message": "The specified capacity '60' of account deployment is bigger than available capacity '0' for UsageName 'Tokens Per Minute (thousands) - Text-Davinci-003'."}
```

### エラーの説明
[Azure OpenAI Serviceのクォータ](https://learn.microsoft.com/azure/cognitive-services/openai/how-to/quota)上限以上のキャパシティを要求した場合にこのエラーが出ます。

### 解決方法
解決方法としては、以下が考えられます
1. Delete（削除）されているリソースのPurge（消去）
2. Quota要求量を減らす
3. 別のリージョンに作成する
4. 既存のリソースのQuotaを下げる
5. 申請してQuota上限を上げてもらう

#### 1. Delete（削除）されてリソースのPurge（消去）
Azure OpenAI Serviceのリソースを削除してから48時間以内の場合、論理削除状態でありQuotaも使われている状態である可能性があります。その場合、[リソースのPurge（消去）](https://learn.microsoft.com/ja-jp/azure/cognitive-services/manage-resources?tabs=azure-portal#purge-a-deleted-resource)することにより使用しているQuotaを下げることができます。

#### 2. Quota要求量を減らす
Bicepの場合は以下のように、`sku`の`capacity`を指定することでQuota要求量を減らすことができます。

呼び出し側
```Bicep
    deployments: [
      {
        name: gptDeploymentName
        model: {
          format: 'OpenAI'
          name: gptModelName
          version: '1'
        }
        sku: {
          name: 'Standard'
          capacity: aoaiCapacity
        }
      }
      {
        name: chatGptDeploymentName
        model: {
          format: 'OpenAI'
          name: chatGptModelName
          version: '0301'
        }
        sku: {
          name: 'Standard'
          capacity: aoaiCapacity
        }
      }
    ]
```

呼び出されるmodule側
```Bicep
resource deployment 'Microsoft.CognitiveServices/accounts/deployments@2023-05-01' = [for deployment in deployments: {
  parent: account
  name: deployment.name
  sku: deployment.sku
  properties: {
    model: deployment.model
    raiPolicyName: contains(deployment, 'raiPolicyName') ? deployment.raiPolicyName : null
  }
}]
```
※accounts/deploymentsは必ず@2023-05-01を使うようにしてください


