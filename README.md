[![static-analysis](https://github.com/Azure-Samples/jp-azureopenai-samples/workflows/static-analysis/badge.svg)](https://github.com/Azure-Samples/jp-azureopenai-samples/actions/workflows/static-analysis.yml)

# Azure OpenAI Samples Japan
Azure OpenAIを活用したアプリケーション実装のリファレンスを目的として、アプリのサンプル（リファレンスアーキテクチャ、サンプルコードとデプロイ手順）を無償提供しています。 本サンプルは、日本マイクロソフトの社員有志により作成・公開しています（This repository contains sample applications that leverage Azure OpenAI with a focus on use cases for the Japan market）

## 公開サンプル一覧 (Samples included)
| タイトル      | README      |
| ------------- | ------------- |
| 1. コールセンター向け AI アシスタント  | [Link](https://github.com/Azure-Samples/jp-azureopenai-samples/tree/main/1.call-center/README.md)  |
| 2. 料理メニューの提案  | [Link](https://github.com/Azure-Samples/jp-azureopenai-samples/tree/main/2.recipe-adviser/README.md)  |
| 3. 目標達成アシスタント  | [Link](https://github.com/Azure-Samples/jp-azureopenai-samples/tree/main/3.goal-achievement-adviser/README.md)  |
| 4. 企業分析  | [Link](https://github.com/Azure-Samples/jp-azureopenai-samples/tree/main/4.company-research/README.md)  |
| 5. 企業内向けChatと社内文書検索  | [Link](https://github.com/Azure-Samples/jp-azureopenai-samples/tree/main/5.internal-document-search/README.md)  |
| 6. 共通ガイド  | [Link](https://github.com/Azure-Samples/jp-azureopenai-samples/tree/main/6.azureopenai-landing-zone-accelerator/README.md)  |

## Getting Started
### 前提知識
- **Azureの基礎**: Azure Portalの使い方、Azure CLIの使い方、Azureリソースの概念、RBAC等のAzureの基礎が前提知識になります。自信がない場合は、[Microsoft Azure Virtual Training Day: Azureの基礎](https://www.microsoft.com/ja-jp/events/top/training-days/azure?activetab=pivot:azure%E3%81%AE%E5%9F%BA%E7%A4%8Etab)等の活用を推奨します。
- **Azure OpenAI Serviceの基礎**: Azure OpenAI Serviceとは何かを理解している必要があります。[Azure OpenAI Developers セミナー](https://www.youtube.com/watch?v=ek3YWrHD76g)をご覧いただければ、最低限の基礎は身に付きます。
- **PowerShellやBash等のコマンドラインツールの使い方の基礎**: 自信がない場合は、[Introduction to PowerShell](https://learn.microsoft.com/training/modules/introduction-to-powershell/)や[Introduction to Bash](https://learn.microsoft.com/training/modules/bash-introduction/)をご活用ください
- **VS Code等のコードエディタの使い方の基礎**: 自信がない場合は、[Introduction to Visual Studio Code](https://learn.microsoft.com/training/modules/introduction-to-visual-studio-code/)をご活用ください
 
### サンプルアプリケーションのデプロイ
日本語: 各サンプルのREADMEをご参照ください。
English: Please refer to the README for each of the samples.

### 本番稼働を視野にいれる場合
本番稼働（や本番に近い検証環境等）を視野にいれる場合、様々な考慮事項があります。考えられる考慮事項は[Cloud Adoption Framework](https://learn.microsoft.com/azure/cloud-adoption-framework/overview)や[Well-Architected Framework](https://learn.microsoft.com/azure/well-architected/)にまとめられていますが、考慮事項は多岐にわたるので、状況（例: シナリオ、企業の事情）に応じて重要度や緊急度等をもとにした優先順位付けが必要になります。例えば、社内文書検索シナリオではプライベートネットワークを考慮した設計が重要になることが多くなると推測される一方、料理メニューの提案シナリオにおいてはエンドユーザのニーズに合わせて柔軟にアプリケーションに機能追加をしていくことが重要になることが推測されます。

### バージョン切り替え

本サンプルでは、過去のバージョンを使用しているユーザがいることを想定し、タグでアプリケーションのバージョンを管理しています。
各バージョンにおける詳しい内容については、[リリースノート](https://github.com/Azure-Samples/jp-azureopenai-samples/releases) をご確認ください。
以下の手順で、特定のcommit時のバージョンを切り替えることができます。

```sh
git checkout -b <ブランチ名> refs/tags/<タグ名>
```

## 制限事項
本レポジトリの内容の使用においては、次の制限、制約をご理解の上、活用ください。
+ 目的外利用の禁止  
本レポジトリは Microsoft Azure 上において、システムやソリューションの円滑かつ安全な構築に資することを目的に作成されています。この目的に反する利用はお断りいたします。
+ フィードバック  
本レポジトリの記載内容へのコメントやフィードバックをいただけます場合は、担当の日本マイクロソフト社員にご連絡ください。なお、個別質問への回答やフィードバックへの対応はお約束できないことを、ご了承いただけますようお願い申し上げます。
+ 公式情報の確認  
本レポジトリは日本マイクロソフトの有志のエンジニアによって作成されたものです。そのため、この記載内容は Microsoft として公式に表明されたものではなく、日本マイクロソフトおよび米国 Microsoft Corporation は一切の責任を負いません。また、本書の記載内容について Azure サポートへお問い合わせいただいても、回答することはできません。  
Microsoft Azure の公式情報については、Azure のドキュメントをご確認ください。
+ 免責  
本レポジトリの記載内容によって発生したいかなる損害についても、日本マイクロソフトおよび米国 Microsoft Corporation は一切の責任を負いません。

## Resources
- [What is Azure OpenAI?](https://learn.microsoft.com/en-us/azure/cognitive-services/openai/overview)
- [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct)
- [Security Reporting Instructions](https://docs.opensource.microsoft.com/content/releasing/security.html)

## Trademarks
Trademarks This project may contain trademarks or logos for projects, products, or services. Authorized use of Microsoft trademarks or logos is subject to and must follow [Microsoft's Trademark & Brand Guidelines](https://www.microsoft.com/en-us/legal/intellectualproperty/trademarks/usage/general). Use of Microsoft trademarks or logos in modified versions of this project must not cause confusion or imply Microsoft sponsorship. Any use of third-party trademarks or logos are subject to those third-party’s policies.
