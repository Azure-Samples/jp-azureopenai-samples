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
| [Python 3+](https://www.python.org/downloads/) | `python --version` | 3.9 以降 |
| pip ( Pythonと一緒にインストール ) | `pip --version` | 23.1 以降 |
| [Node.js](https://nodejs.org/en/download/) | `node --version` | 16 以降 |
| [Git](https://git-scm.com/downloads) | `git --version` | 2.33 以降 |


### 権限
実行するユーザの AAD アカウントは、`Microsoft.Authorization/roleAssignments/write` 権限を持っている必要があります。この権限は [ユーザーアクセス管理者](https://learn.microsoft.com/azure/role-based-access-control/built-in-roles#user-access-administrator) もしくは [所有者](https://learn.microsoft.com/azure/role-based-access-control/built-in-roles#owner)が保持しています。  
`az role assignment list --assignee <your-Azure-email-address> --subscription <subscription-id> --output table`

## Azureのリソース作成
```PowerShell
$ENV:SUB = "your-subscription-id"
$ENV:EMAIL = "your-email" # 作業者のユーザープリンシパル名
$Env:AZURE_PRINCIPAL_ID = az ad user show --id $ENV:EMAIL -o tsv --query id # 作業者のObjectId

$ENV:LOC = "francecentral" # The location to store the deployment metadata and to deploy resources
$ENV:DEP_NAME = "depnametemp3" # The deployment name
$ENV:AZURE_ENV_NAME = "azureenvnametemp" # リソースグループ名のSuffix (rg-$ENV:AZURE_ENV_NAMEになる)

cd ../../infra
az deployment sub create --name $ENV:DEP_NAME --location $ENV:LOC --template-file main.bicep --parameters principalId=$ENV:AZURE_PRINCIPAL_ID environmentName=$ENV:AZURE_ENV_NAME location=$ENV:LOC
```

## アプリケーションコードのビルドとデプロイ
### フロントエンドのビルド
```
cd jp-azureopenai-samples/5.internal-document-search/src/frontend
npm install
npm run build
```

### Pythonコードのデプロイ
```
$ENV:AZURE_WEBAPP_RESOURCE_GROUP = "rg-${ENV:AZURE_ENV_NAME}"
$ENV:WEBAPP_NAME = "app service name"

cd jp-azureopenai-samples/5.internal-document-search/src/backend
zip -r app.zip .
az webapp deployment source config-zip --resource-group $ENV:AZURE_WEBAPP_RESOURCE_GROUP --name $ENV:WEBAPP_NAME --src ./app.zip
```

コマンドの実行が終了すると、アプリケーションにアクセスする為の URL が表示されます。この URL をブラウザで開き、サンプルアプリケーションの利用を開始してください
> 注意: アプリケーションのデプロイ完了には数分かかることがあります。"Python Developer" のウェルカムスクリーンが表示される場合は、数分待ってアクセスし直してください。

## データの投入（data配下のPDFを利用して Search Index を作成）
### 環境変数の設定
```PowerShell
$env:AZURE_COSMOSDB_ACCOUNT = "cosmosdb-name"
$env:AZURE_COSMOSDB_RESOURCE_GROUP = "rg-${ENV:AZURE_ENV_NAME}"
$env:BACKEND_IDENTITY_PRINCIPAL_ID = "app serviceのManaged IdentityのObject ID"

$env:AZURE_STORAGE_ACCOUNT = "storagae account name"
$env:AZURE_STORAGE_CONTAINER = "content"
$env:AZURE_SEARCH_SERVICE = "search service name"
$env:AZURE_SEARCH_INDEX = "gptkbindex"
$env:AZURE_SEARCH_KEY = "xxx"
$env:AZURE_FORMRECOGNIZER_SERVICE = "form recognizer name"
$env:AZURE_FORMRECOGNIZER_KEY = "xxx"
$env:AZURE_TENANT_ID = "Azure AD tenant ID"
```

### Create and assign Cosmos DB data actions roles
```PowerShell
cd jp-azureopenai-samples/5.internal-document-search

Write-Host "Create and assign Cosmos DB data actions roles"
$roleId = az cosmosdb sql role definition create --account-name $env:AZURE_COSMOSDB_ACCOUNT --resource-group $env:AZURE_COSMOSDB_RESOURCE_GROUP --body ./scripts/cosmosreadwriterole.json --output tsv --query id

# So that the app service can access Cosmos DB
az cosmosdb sql role assignment create --account-name $env:AZURE_COSMOSDB_ACCOUNT --resource-group $env:AZURE_COSMOSDB_RESOURCE_GROUP --scope / --principal-id $env:BACKEND_IDENTITY_PRINCIPAL_ID --role-definition-id $roleId

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

Write-Host 'Creating python virtual environment "scripts/.venv"'
Start-Process -FilePath ($pythonCmd).Source -ArgumentList "-m venv ./scripts/.venv" -Wait -NoNewWindow

$venvPythonPath = "./scripts/.venv/scripts/python.exe"
if (Test-Path -Path "/usr") {
  # fallback to Linux venv path
  $venvPythonPath = "./scripts/.venv/bin/python"
}

Write-Host 'Installing dependencies from "requirements.txt" into virtual environment'
Start-Process -FilePath $venvPythonPath -ArgumentList "-m pip install -r ./scripts/requirements.txt" -Wait -NoNewWindow

Write-Host 'Running "prepdocs.py"'
$cwd = (Get-Location)
Start-Process -FilePath $venvPythonPath -ArgumentList "./scripts/prepdocs.py $cwd/data/* --storageaccount $env:AZURE_STORAGE_ACCOUNT --container $env:AZURE_STORAGE_CONTAINER --searchservice $env:AZURE_SEARCH_SERVICE --searchkey $env:AZURE_SEARCH_KEY --index $env:AZURE_SEARCH_INDEX --formrecognizerservice $env:AZURE_FORMRECOGNIZER_SERVICE --formrecognizerkey $env:AZURE_FORMRECOGNIZER_KEY --tenantid $env:AZURE_TENANT_ID -v --managedidentitycredential" -Wait -NoNewWindow
```

## アプリケーションのローカル実行
アプリケーションをローカルで実行する場合には、以下のコマンドを実行してください。`azd up`で既に Azure 上にリソースがデプロイされていることを前提にしています。

1. `azd login` を実行する。
2. `src` フォルダに移動する。
3. `./start.ps1` もしくは `./start.sh` を実行します。

#### VS Codeでのデバッグ実行
1. `src\backend`フォルダに異動する
2. `code .`でVS Codeを開く
3. Run>Start Debugging または F5

### FrontendのJavaScriptのデバッグ
1. src/frontend/vite.config.tsのbuildに`minify: false`を追加
2. ブラウザのDeveloper tools > Sourceでブレイクポイントを設定して実行