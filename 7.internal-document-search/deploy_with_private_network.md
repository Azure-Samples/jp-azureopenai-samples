# Chat+社内文書検索

## 概要
5章のChat+社内文書検索シナリオのインターネットアクセス不要なセキュアな通信が可能となるようなアーキテクチャで構成したものです。

## 5章との差分

#### リソース追加・変更内容

- App Service Environment
  - アプリのデプロイ先をApp Serviceから App Service Evironmentにしています。
- 仮想デスクトップ
  - アプリクライアントへアクセスするための環境として仮想デスクトップを配置しています。
- Private Endpoint
  - Cognitive Service, Azure OpenAI Service, Form Recognizer, Storage AccountをAzure内で通信させるために、プライベートエンドポイントを配置しています。
- Azure Virtual Network
  - インターネットアクセスから遮断するため、全てのリソースをVnet内に配置しています。
- サブネット
  - 仮想デスクトップ、App Service Environment、プライベートエンドポイント群の3つに対してそれぞれサブネットを配置しています。

IaCとして追加・更新したファイルは以下の通りです。

- ./infra/core/network/privateEndpoint.bicep
- ./infra/core/network/subnet.bicep
- ./infra/core/network/vnet.bicep
- ./infra/main.bicep


## セットアップガイド

5章の azdコマンドによるデプロイと同じ手順でデプロイを行うことが可能です。
