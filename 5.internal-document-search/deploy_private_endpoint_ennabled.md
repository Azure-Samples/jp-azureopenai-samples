## デプロイ手順
閉域網でのデプロイを実行するには、以下の手順でデプロイします。

1. `./infra/main.parameters.json`の`isPrivateEndpointEnabled`を`true`に設定します。

2. azd CLIを用いてリソースのデプロイの実行を行います。

```bash
azd up
```

3. デプロイ完了後、以下の各リソースを閉域網に変更します。

- Azure Cosmos DB
- Azure Storage Account
- Azure App Service
- Azure Cognitive Search


4. デプロイされているApp Serviceの `既定のドメイン` をブラウザから開き、以下のようにアクセス制限がかかっていることを確認します。

![403の画面](./assets/private_403.png)

5. リソースグループにデプロイされているVirtual Machine内に以下の認証情報を用いてremote desktop接続を行います。

```
接続先：Virtual MachineのパブリックIPアドレス
ユーザ名：azureuser
パスワード：Admin#123456#
```

6. Virtual Machine内での中でブラウザを開き、App Serviceの `既定のドメイン` へのアクセスが可能なことを確認してください。

