# 企業分析

Azure OpenAIを活用したアプリケーションは、法人営業がお客様先へ初回訪問する際に必要となる企業分析にも役に立ちます。

企業分析をしたい人がチャットのUIで気になることをアプリケーションに伝えることで、アプリケーションが様々な情報源から情報収集をして、企業分析に役に立たせることができます。また、収集した情報やそこから得たインサイトをレポート形式に出力することができます。

情報の取得先は、例えば以下の3つが考えられます
１．会社名などの一般的なスタティック情報
２．仕掛中案件など社内CRM等の情報
３．GPTに聞く情報

### 主な機能

1. 企業情報名での企業情報の検索ができます
1. チャット形式で、より詳細な企業情報のの分析ができます
1. レポート形式で、より詳細な企業情報のの分析ができます

### アプリケーション画面

![Chat screen](docs/demo-chat.png)
![Report screen](docs/demo-report.png)

### コンポーネントとデータフロー
WEB アプリケーションを Azure App Service でホストしたコンポーネントとデータフローの図となります。

![Solution](docs/diagram.png)

## セットアップガイド

本セットアップガイドは、以下の順番で記載しています
1. [ローカル作業環境のセットアップ](#ローカル作業環境のセットアップ)
1. [クラウド実行環境のセットアップ](#クラウド実行環境のセットアップ)
1. [ローカルデバッグ環境のセットアップ](#ローカルデバッグ環境のセットアップ)

### ローカル作業環境のセットアップ
以下がインストールされている環境をご準備ください
- bash
- git
- Azure CLI
- Visual Studio Code
    - Azure App Service 拡張機能 
    - Python 拡張機能
- Python 3.10

筆者はWindows 11上のWSL2環境を中心に検証をしていますが、上記がインストールされている環境であればセットアップはできる想定でガイドを書いています。

### クラウド実行環境のセットアップ
以下は "検証用途の最小構成" を示しています。

|  サービス名  |  SKU  | Note |
| ---- | ---- | ---- |
| Azure App Service  |  Standard (S1)  | Python 3.10 |
| Azure OpenAI Service |  Standard (S0)  | gpt-35-turbo, text-davinci-003, text-embedding-ada-002 |
| Azure Cache for Redis | Enterprise (E10) | RediSearch |

### Azureリソースのプロビジョニング
```bash
git clone https://github.com/Azure-Samples/jp-azureopenai-samples

cd jp-azureopenai-samples/4.company-research
cd infra

PRINCIPAL_ID=YOUR-PRINCIPAL-ID

az deployment sub create --parameter environmentName=company-research --parameter location=japaneast --parameter openAiResourceGroupLocation=eastus --parameter principalId=$PRINCIPAL_ID --location japaneast --template-file ./main.bicep
```
YOUR-PRINCIPAL-IDの取得方法例: Azure Portal > Azure AD > Users > 自分の名前で検索 > Object IDをコピー

### 2. App Service 構成 - 環境変数の設定

Azure ポータルで App Service の [構成] メニューを選択し、開発環境の .env/launch.json に定義してある環境変数を設定します。

![App Service 構成](doc/appservice_configuration.jpg)


### 3. アクセス制御 (IAM) の構成

Azure ポータルで、各バックエンドサービスの [アクセス制御 (IAM)] メニューを開き App Service の Managed ID に該当する以下の権限（ロール）を割り当てます。 

|  サービス名  |  ロール  | 
| ---- | ---- |
| Azure OpenAI Service |  Cognitive Services OpenAI User  | 

### 4. WEB アプリケーションを App Service へデプロイ

VSCode の左側ペインより Azure アイコンを選択し、該当する [App Service] に対して [Deploy to Web App...] にてアプリケーションを展開します。

約4分かかります。

![Deploy](docs/deploy.jpg)

# ナレッジベースに企業の最新情報を登録
[ナレッジベースに企業の最新情報を登録](scripts/README.md)

### 開発環境のセットアップ

#### 1. アクセス制御 (IAM) の構成

VSCode の Azure 拡張機能で Azure へサインインする事で、デバッグ実行の際にサインインユーザーの Credential が DefaultAzureCredential となります。 

Azure ポータルで各バックエンドサービスの [アクセス制御 (IAM)] メニューを開き、サインインユーザーに該当する以下の権限（ロール）を割り当てます。 

|  サービス名  |  ロール  | 
| ---- | ---- |
| Azure OpenAI Service |  Cognitive Services OpenAI User  | 

#### 2. ローカルデバッグ用の環境変数設定

##### Option 1: .env
```
cd app\backend
cp .env.template .env
```
.envファイルの値を環境に合わせて設定します。

##### Option 2: WIP
`.vscode/launch.json` ファイルで <Your ...> の値を環境に合わせて設定します。

```json
"env": {
    "FLASK_APP": "${workspaceFolder}/app.py",
    "FLASK_DEBUG": "1",
    "AZURE_OPENAI_API_TYPE": "azure",
    ...
}
```

#### 3. モジュールのインストール

```bash
pip install -r requirements.txt
```

#### 4. デバッグ実行

VSCode からデバッグ実行を開始します。

Running on http://127.0.0.1:5000

#### 動作確認
クラウドに下記サービスがデプロイされている必要があります。

|  サービス名  |  SKU  | Note |
| ---- | ---- | ---- |
| Azure OpenAI Service |  Standard  | gpt-35-turbo, text-davinci-003, text-embedding-ada-002 |
| Azure Cache for Redis | Enterprise | |
