# トラブルシューティングガイド (Troubleshooting Guide)
## Table of Contents
1. [InsufficientQuota](#InsufficientQuota)
2. [InvalidTemplateDeployment](#InvalidTemplateDeployment)
## InsufficientQuota
### エラーメッセージ例 (Example error message)
```
{"code": "InsufficientQuota", "message": "The specified capacity '60' of account deployment is bigger than available capacity '0' for UsageName 'Tokens Per Minute (thousands) - Text-Davinci-003'."}
```

### エラーの説明
[Azure OpenAI Serviceのクォータ](https://learn.microsoft.com/azure/cognitive-services/openai/how-to/quota)上限以上のキャパシティを要求した場合にこのエラーが出ます。

### 解決方法
解決方法としては、以下が考えられます
1. Quotaを圧迫している既存リソースのPurge（消去）
2. Quota要求量を減らす
3. 別のリージョンに作成する
4. 既存のリソースのQuotaを下げる

#### 1. Quotaを圧迫している既存リソースのPurge（消去）
同サブスクリプション・リージョン内の同じ種類のモデルのリソースを削除することでQuotaを開放することができます。ただし、Azure OpenAI Serviceのリソースを削除してから48時間以内の場合、論理削除状態でありQuotaも使われている状態である可能性があります。その場合、[リソースのPurge（消去）](https://learn.microsoft.com/ja-jp/azure/cognitive-services/manage-resources?tabs=azure-portal#purge-a-deleted-resource)することにより使用しているQuotaを下げることができます。

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

#### 3. 別のリージョンに作成する
Quotaはサブスクリプション内のリージョン毎に設定されているため、他のリージョンに作成することで既存リソースに割り当てたQuotaの影響を受けずにデプロイすることが可能です。

#### 4. 既存のリソースのQuotaを下げる
既存リソースのQuotaを以下のような手順で下げることが可能です。
1. Azure OpenAIアカウントを開く
2. 「モデルとデプロイ」を選択（Azure OpenAI Studio画面が開きます）
3. 「管理」＞「クォータ」を選択
4. デプロイされたモデルのリストからQuotaを変えたいモデルを選択
5. 「デプロイの編集」＞「詳細設定オプション」からQuotaを変更
6. 「保存して終了」を選択
7. 
## InvalidTemplateDeployment
### エラーメッセージ例 (Example error message)
```
ERROR: deployment failed: failing invoking action 'provision', error deploying infrastructure: deploying to subscription:

Deployment Error Details:
InvalidTemplateDeployment: The template deployment 'openai' is not valid according to the validation procedure. The tracking id is 'xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx'. See inner errors for details.
DeploymentModelNotSupported: Creating account deployment is not supported by the model 'text-davinci-003'. This is usually because there are better models available for the similar functionality.
```
### エラーの説明
対象のAzure OpenAIモデルがデプロイできない。

### 解決方法
別のモデルとバージョンを指定（例: text-davinci-003のversion=1からのgpt-35-turboのversion=0301）
