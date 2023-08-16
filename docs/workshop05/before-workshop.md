# Chat+社内文書検索 ワークショップの実施環境準備

## Azure サブスクリプション

このワークショップを実行するには、 Azure OpenAI Service へのアクセスを有効にした Azure サブスクリプションが必要です。
アクセスは[こちら](https://aka.ms/oaiapply)からリクエストできます。
また開発者がワークショップで使用するユーザーアカウントには、Azure サブスクリプションに対する `Microsoft.Authorization/roleAssignments/write` の権限が必要です。
この権限は [所有者](https://learn.microsoft.com/ja-jp/azure/role-based-access-control/built-in-roles#owner) や [ユーザー アクセス 管理者](https://learn.microsoft.com/ja-jp/azure/role-based-access-control/built-in-roles#user-access-administrator) RBAC ロールに含まれています。


## VS Code Dev Container の場合

?> Visual Studio Code Dev Container を使用する場合には Windows PC / MacOS のどちらでも実施可能です。

```
準備中
```

## Windows PC を使用する場合

?> Windows PC に各種ソフトウェアをインストールする場合は、インストール済みのバージョンとの衝突にご注意ください。

### Azure CLI

Azure CLI version 2.50.0 以降が推奨です。
以下のコマンドでバージョンを確認してください。

```pwsh
az --version
```
```pwsh
# 出力結果の例
azure-cli                         2.49.0 *
```

バージョンが古い場合は、以下のコマンドでアップデートしてください。

```pwsh
az upgrade
```

インストールされていない場合は、以下のコマンドでインストールしてください。

```pwsh
winget install Microsoft.AzureCLI
```

### Azure Developer CLI

Azure Developer CLI version 1.0.2 以降が推奨です。
以下のコマンドでバージョンを確認してください。

```pwsh
azd version
```
```pwsh
# 出力結果の例
azd version 1.2.0 (commit 99ea7577f0df0df2ba34b677da189fafba18c0f7)
```

インストールされていない場合は、以下のコマンドでインストールしてください。

```pwsh
winget install Microsoft.Azd
```

### Python 3

Python version 3.11 以降が推奨です。
以下のコマンドでバージョンを確認してください。

```pwsh
python --version
```
```pwsh
# 出力結果の例
Python 3.11.4
```

インストールされていない場合は、以下のコマンドでインストールしてください。

```pwsh
winget install Python.Python.3.11 
```
https://learn.microsoft.com/ja-jp/windows/python/beginners

### Node.js

Node.js version 14.18 以降が推奨です。
以下のコマンドでバージョンを確認してください。

```pwsh
node --version
```
```pwsh
# 出力結果の例
v18.16.1
```

### Git

Git のバージョンは以下で確認できます。

```pwsh
git --version
```
```pwsh
# 出力結果の例
git version 2.41.0.windows.3
```

インストールされていない場合は、以下のコマンドでインストールしてください。

```pwsh
winget install Git.Git
```

### PowerShell (pwsh)

PowerShell version 7 以降が推奨です。
以下のコマンドでバージョンを確認してください。

```pwsh
pwsh --version
```
```pwsh
# 出力結果の例
PowerShell 7.3.6
```

インストールされていない場合は、以下のコマンドでインストールしてください。

```pwsh
winget install Microsoft.PowerShell
```

### Visual Studio Code

インストールされている Visual Studio Code のバージョンを確認します。

```pwsh
code --version
```
```pwsh
# 出力結果の例
1.81.1
6c3e3dba23e8fadc360aed75ce363ba185c49794
x64
```

インストールされていない場合は、以下のコマンドでインストールしてください。

```pwsh
winget install Microsoft.VisualStudioCode
```


## コンテンツ のセットアップ

###  サンプルコードの取得

このリポジトリをクローンします。

```pwsh
git clone https://github.com/ayuina/jp-azureopenai-samples.git
```

### Visual Studio Code で開く

`Chat+社内文書検索` のサンプルを含むディレクトリを Visual Studio Code で開きます

```pwsh
code .\jp-azureopenai-samples\5.internal-document-search\
```

以降のコマンドは Visual Studio Code の pwsh ターミナルで実行してください。