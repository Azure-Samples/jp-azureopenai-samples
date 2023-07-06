# Chat+社内文書検索

## 概要
このデモは、ChatGPTライクなインターフェースを使用して企業の社内文書を検索するアプリケーションの実装パターンです。デモアプリを利用するためには、Azure Open AI の ChatGPT(gpt-35-turbi)モデルと、Azure Cognitive Search、他にいくつかのリソースの作成が必要です。

このリポジトリでは、サンプルデータに[厚生労働省のモデル就業規則](https://www.mhlw.go.jp/stf/seisakunitsuite/bunya/koyou_roudou/roudoukijun/zigyonushi/model/index.html)を使用しています。

デモアプリは以下のように動作します。

## Architecture
![RAG Architecture](assets/appcomponents.png)

## UI
![Chat screen](assets/chatscreen.png)

## セットアップガイド

> **重要:** このサンプルをデプロイするには、**Azure Open AIサービスが有効になっているサブスクリプションが必要です**。Azure Open AIサービスへのアクセス申請は[こちら](https://aka.ms/oaiapply)から行ってください。

### 事前準備

#### クラウド実行環境
このデモをデプロイすると以下のリソースがAzureサブスクリプション上に作成されます。
| サービス名 | SKU | Note |
| --- | --- | --- |
|Azure App Service|B1||
|Azure OpenAI Service|S0|text-davinchi-003,gpt-3.5-turbo|
|Azure Cognitive Search|S0||
|Azure Cosmos DB|プロビジョニング済みスループット||
|Azure Form Recgonizer|S0||
|Azure Blob Storage|汎用v2|ZRS|

#### ローカル開発環境
このデモをデプロイするためには、ローカルに以下の開発環境が必要です。
> **重要** このサンプルはWindowsもしくはLinux環境で動作します。ただし、WSL2の環境では正常に動作しません。
- [Azure Developer CLI](https://aka.ms/azure-dev/install)
- [Python 3+](https://www.python.org/downloads/)
    - **重要**: Windows環境では、pythonおよびpipをPath環境変数に含める必要があります。
    - **重要**: `python --version` で現在インストールされているPythonのバージョンを確認することができます。 Ubuntuを使用している場合、`sudo apt install python-is-python3` で `python` と `python3`をリンクさせることができます。    
- [Node.js](https://nodejs.org/en/download/)
- [Git](https://git-scm.com/downloads)
- [Powershell 7+ (pwsh)](https://github.com/powershell/powershell) - Windowsで実行する場合のみ
   - **重要**: `pwsh.exe` がPowerShellコマンドとして実行できることを確認して下さい。

>注意: 実行するユーザのAADアカウントは、`Microsoft.Authorization/roleAssignments/write` 権限を持っている必要があります。この権限は [ユーザーアクセス管理者](https://learn.microsoft.com/azure/role-based-access-control/built-in-roles#user-access-administrator) もしくは [所有者](https://learn.microsoft.com/azure/role-based-access-control/built-in-roles#owner)が保持しています。  

### インストール

#### プロジェクトの初期化

1. このリポジトリをクローンし、フォルダをターミナルで開きます。
1. `azd auth login`を実行します。
1. `azd init`を実行します。
    * 現在、このサンプルは必要なAzure Open AIのモデルがデプロイ可能な**米国東部**もしくは**米国中南部**リージョンにデプロイ可能です。最新の情報は[こちら](https://learn.microsoft.com/en-us/azure/cognitive-services/openai/concepts/models)を参考にしてください。

#### スクラッチでの開始

新規に環境をデプロイする場合は、以下のコマンドを実行してください。

1. `az login`と`az account set -s YOUR_SUBSCRIPTION_NAME`後に、`az ad user show --id your_account@your_tenant -o tsv --query id` を実行して、操作をするユーザの AAD アカウントのオブジェクトID を取得します。
1. 取得したオブジェクトID を環境変数`AZURE_PRINCIPAL_ID`にセットします。
    - Windows 環境で実行している場合は、`$Env:AZURE_PRINCIPAL_ID="Your Object ID"`を実行します。
    - Linux 環境で実行している場合は、`export AZURE_PRINCIPAL_ID="Your Object ID"`を実行します。
1. `azd up` を実行します。- このコマンドを実行すると、Azure上に必要なリソースをデプロイし、アプリケーションのビルドとデプロイが実行されます。また、`./data`配下の PDF を利用して Search Index を作成します。
1. コマンドの実行が終了すると、アプリケーションにアクセスする為の URL が表示されます。この URL をブラウザで開き、サンプルアプリケーションの利用を開始してください。  

コマンド実行結果の例：

!['Output from running azd up'](assets/endpoint.png)
    
> 注意: アプリケーションのデプロイ完了には数分かかることがあります。"Python Developer"のウェルカムスクリーンが表示される場合は、数分待ってアクセスし直してください。

#### アプリケーションのローカル実行
アプリケーションをローカルで実行する場合には、以下のコマンドを実行してください。`azd up`で既にAzure上にリソースがデプロイされていることを前提にしています。

1. `azd login`を実行する。
2. `src`フォルダに移動する。
3. `./start.ps1` もしくは `./start.sh` を実行します。

### GPT-4モデルの利用
2023年6月現在、GPT-4モデルは申請することで利用可能な状態です。このサンプルはGPT-4モデルのデプロイに対応していますが、GPT-4モデルを利用する場合には、[こちら](https://learn.microsoft.com/ja-jp/azure/cognitive-services/openai/how-to/create-resource?pivots=web-portal#deploy-a-model)を参考に、GPT-4モデルをデプロイしてください。また、GPT-4モデルの利用申請は[こちらのフォーム](https://aka.ms/oai/get-gpt4)から可能です。

GPT-4モデルのデプロイ後、以下の操作を実行してください。

1. このサンプルをデプロイした際に、プロジェクトのディレクトリに`./${環境名}/.env`ファイルが作成されています。このファイルを任意のエディタで開きます。
1. 以下の行を探して、デプロイしたGPT-4モデルのデプロイ名を指定してください。
> AZURE_OPENAI_GPT_4_DEPLOYMENT="" # GPT-4モデルのデプロイ名
AZURE_OPENAI_GPT_4_32K_DEPLOYMENT="" # GPT-4-32Kモデルのデプロイ名

1. `azd up`を実行します。

GPT-4モデルは、チャット機能、文書検索機能のオプションで利用することができます。

### Easy Authの設定（オプション）
必要に応じて、Azure ADに対応したEasy Authを設定します。Easy Authを設定した場合、UIの右上にログインユーザのアカウント名が表示され、チャットの履歴ログにもアカウント名が記録されます。
Easy Authの設定は、[こちら](https://learn.microsoft.com/ja-jp/azure/app-service/scenario-secure-app-authentication-app-service)を参考にしてください。