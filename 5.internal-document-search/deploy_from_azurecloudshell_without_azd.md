# Chat+社内文書検索
一般的なツールが事前にインストール済みであるAzure Cloud Shellからのセットアップする方法を記載します。2023年8月にはazdもAzure Cloud Shellに事前にインストールされるようになる可能性もありますが、2023年7月時点では事前にインストールされていないので、こちらの手順はazdを使わないものとします。

# セットアップガイド
> **重要:** このサンプルをデプロイするには、**Azure Open AI サービスが有効になっているサブスクリプションが必要です**。Azure Open AI サービスへのアクセス申請は[こちら](https://aka.ms/oaiapply)から行ってください。

## 事前準備

### ツール
このデモをデプロイするためには、ローカルに以下の開発環境が必要です。Azure Cloud Shellに、以下が事前にインストールされていることをご確認ください。PowerShellを前提としています。

| ツール名 | 確認コマンド | 推奨バージョン | 
| --- | --- | --- |
| [Azure CLI](https://learn.microsoft.com/cli/azure/install-azure-cli) | `az --version` | 2.50.0 以降 |
| [Python 3+](https://www.python.org/downloads/) | `python --version` | 3.9.14 以降 |
| pip ( Pythonと一緒にインストール ) | `pip --version` | 23.1.2 以降 |
| [Node.js](https://nodejs.org/en/download/) | `node --version` | 16.19.1 以降 |
| [Git](https://git-scm.com/downloads) | `git --version` | 2.33.8 以降 |


### 環境変数設定
以下のように環境変数を設定します。
```PowerShell
$ENV:SUB = "your-subscription-id"
$ENV:USER_ID = "your-id" # 作業者のユーザープリンシパル名
$Env:AZURE_PRINCIPAL_ID = az ad user show --id $ENV:USER_ID -o tsv --query id # 作業者のObjectId

$ENV:LOC = "japaneast" # The location to store the deployment metadata and to deploy resources
$ENV:DEP_NAME = "deployment-name" # The deployment name 
$ENV:AZURE_ENV_NAME = "azureenvnametemp" # リソースグループ名のSuffix (rg-$ENV:AZURE_ENV_NAMEになる)
```

### 権限確認
実行するユーザの AAD アカウントは、`Microsoft.Authorization/roleAssignments/write` 権限を持っている必要があります。この権限は [ユーザーアクセス管理者](https://learn.microsoft.com/azure/role-based-access-control/built-in-roles#user-access-administrator) もしくは [所有者](https://learn.microsoft.com/azure/role-based-access-control/built-in-roles#owner)が保持しています。  
```
az role assignment list --assignee $ENV:USER_ID --subscription $ENV:SUB --output table
```

### コードの取得
```PowerShell
mkdir <作業用フォルダ名>
cd <作業用フォルダ名>
git clone https://github.com/Azure-Samples/jp-azureopenai-samples
```

## Azureのリソース作成
以下のコマンドを用いて、Azureのリソースを作成します。
```PowerShell
cd jp-azureopenai-samples/5.internal-document-search/infra

az deployment sub create --name $ENV:DEP_NAME --location $ENV:LOC --template-file main.bicep --parameters principalId=$ENV:AZURE_PRINCIPAL_ID environmentName=$ENV:AZURE_ENV_NAME location=$ENV:LOC
```

`InsufficientQuota`等のエラーについては[トラブルシューティングガイド](../troubleshooting.md)をご参照ください。

## アプリケーションコードのビルドとデプロイ
本アプリケーションは、フロントエンドがJavaScriptで書かれており、バックエンドがPythonで書かれています。まずは、フロントエンドのJavaScriptのコードビルドし、その後にPythonのコードと一緒にAzure Web Appにデプロイします。
### フロントエンドのビルド
`package.json`や`vite.config.ts`に従ってビルドをし、結果を`../backend/static`に出力します。
```PowerShell
cd jp-azureopenai-samples/5.internal-document-search/src/frontend
npm install
npm run build
```

### Pythonコードのデプロイ
ビルドされたフロントエンドのコードと一緒に、PythonのアプリケーションコードをAzure Web Appにデプロイします。
```PowerShell
$ENV:AZURE_WEBAPP_RESOURCE_GROUP = "rg-${ENV:AZURE_ENV_NAME}"
$ENV:WEBAPP_NAME = "xxx" # Azureリソースの作成時に作成されているリソースの名前

cd jp-azureopenai-samples/5.internal-document-search/src/backend
zip -r app.zip .
az webapp deployment source config-zip --resource-group $ENV:AZURE_WEBAPP_RESOURCE_GROUP --name $ENV:WEBAPP_NAME --src ./app.zip
```

コマンドの実行が終了すると、アプリケーションにアクセスする為の URL が表示されます。この URL をブラウザで開き、サンプルアプリケーションの利用を開始してください
> 注意: アプリケーションのデプロイ完了には数分かかることがあります。"Python Developer" のウェルカムスクリーンが表示される場合は、数分待ってアクセスし直してください。

### Create and assign Cosmos DB data actions roles
App ServiceがCosmos DBにアクセスするための権限付与が必要になります。付与しない場合、「企業向けChat」を利用しようとした場合に以下の様なエラーになります。
`Error: (Forbidden) Request blocked by Auth xxx : Request is blocked because principal [xxx] does not have required RBAC permissions to perform action`

```PowerShell
$env:AZURE_COSMOSDB_ACCOUNT = "xxx" # Azureリソースの作成時に作成されているリソースの名前
$env:AZURE_COSMOSDB_RESOURCE_GROUP = "rg-${ENV:AZURE_ENV_NAME}"
$env:BACKEND_IDENTITY_PRINCIPAL_ID = "app serviceのManaged IdentityのObject ID"

$env:BACKEND_IDENTITY_PRINCIPAL_ID = "app serviceのManaged IdentityのObject ID" # Azure PortalからApp ServiceのObejct IDを取得

cd jp-azureopenai-samples/5.internal-document-search

$roleId = az cosmosdb sql role definition create --account-name $env:AZURE_COSMOSDB_ACCOUNT --resource-group $env:AZURE_COSMOSDB_RESOURCE_GROUP --body ./scripts/cosmosreadwriterole.json --output tsv --query id

# So that the app service can access Cosmos DB
az cosmosdb sql role assignment create --account-name $env:AZURE_COSMOSDB_ACCOUNT --resource-group $env:AZURE_COSMOSDB_RESOURCE_GROUP --scope / --principal-id $env:BACKEND_IDENTITY_PRINCIPAL_ID --role-definition-id $roleId
```

ここまでの手順で、「企業向けChat」の機能が使えるようになりますが、社内文書データの投入ができていないので、「社内文書検索」機能を使おうとすると`Error: () The index 'gptkbindex' for service 'xxx' was not found`というエラーになります。

## データの投入（data配下のPDFを利用して Search Index を作成）
`data/`にあるPDFファイルをAzure Blob Storageにアプロードし、そのデータを使ってAzure Searchのインデックスを作成します。
### 環境変数の設定
```PowerShell
$env:AZURE_STORAGE_ACCOUNT = "xxx" # Azureリソースの作成時に作成されているリソースの名前
$env:AZURE_STORAGE_CONTAINER = "content" # 固定値
$env:AZURE_SEARCH_SERVICE = "xxx" # Azureリソースの作成時に作成されているリソースの名前
$env:AZURE_SEARCH_INDEX = "gptkbindex" # 固定値
$env:AZURE_SEARCH_KEY = "xxx" # Azure PortalからAzure Search ServiceのKeyを取得
$env:AZURE_FORMRECOGNIZER_SERVICE = "xxx" # Azureリソースの作成時に作成されているリソースの名前
$env:AZURE_FORMRECOGNIZER_KEY = "xxx" # Azure PortalからAzure Form RecognizerのKeyを取得
```

### スクリプト実行用にCosmosDB権限付与
```PowerShell
# So that the user can access Cosmos DB for script execution
az cosmosdb sql role assignment create --account-name $env:AZURE_COSMOSDB_ACCOUNT --resource-group $env:AZURE_COSMOSDB_RESOURCE_GROUP --scope / --principal-id $env:AZURE_PRINCIPAL_ID --role-definition-id $roleId
```

### Run prepdocs.py
```PowerShell
cd jp-azureopenai-samples/5.internal-document-search

$pythonCmd = Get-Command python -ErrorAction SilentlyContinue
if (-not $pythonCmd) {
  # fallback to python3 if python not found
  $pythonCmd = Get-Command python3 -ErrorAction SilentlyContinue
}

# Creating python virtual environment "scripts/.venv"
Start-Process -FilePath ($pythonCmd).Source -ArgumentList "-m venv ./scripts/.venv" -Wait -NoNewWindow

$venvPythonPath = "./scripts/.venv/scripts/python.exe"
if (Test-Path -Path "/usr") {
  # fallback to Linux venv path
  $venvPythonPath = "./scripts/.venv/bin/python"
}

# Installing dependencies from "requirements.txt" into virtual environment
Start-Process -FilePath $venvPythonPath -ArgumentList "-m pip install -r ./scripts/requirements.txt" -Wait -NoNewWindow

# Running "prepdocs.py"
$cwd = (Get-Location)
Start-Process -FilePath $venvPythonPath -ArgumentList "./scripts/prepdocs.py $cwd/data/* --storageaccount $env:AZURE_STORAGE_ACCOUNT --container $env:AZURE_STORAGE_CONTAINER --searchservice $env:AZURE_SEARCH_SERVICE --searchkey $env:AZURE_SEARCH_KEY --index $env:AZURE_SEARCH_INDEX --formrecognizerservice $env:AZURE_FORMRECOGNIZER_SERVICE --formrecognizerkey $env:AZURE_FORMRECOGNIZER_KEY -v --managedidentitycredential" -Wait -NoNewWindow
```

データの投入し、Search Indexを作成することで、社内文書検索の機能も使えるようになります。