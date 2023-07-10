# azd up time
19 minutes

# Time until Python app updated on App Service
azd up終了後にすぐにアクセスしても。デフォルトのPythonアプリのまま。
2分後にアクセスしたら、更新されていた（0分~2分後にはアクセスしていない）

# Request blocked by Auth cosmos-xxx
```
Error: (Forbidden) Request blocked by Auth cosmos-t7xd3xtlokx2a : Request is blocked because principal xxx does not have required RBAC permissions to perform action [Microsoft.DocumentDB/databaseAccounts/readMetadata] on resource [/]. Learn more: https://aka.ms/cosmos-native-rbac.
ActivityId: xxx, Microsoft.Azure.Documents.Common/2.14.0
Code: Forbidden
Message: Request blocked by Auth cosmos-t7xd3xtlokx2a : Request is blocked because principal xxx does not have required RBAC permissions to perform action [Microsoft.DocumentDB/databaseAccounts/readMetadata] on resource [/]. Learn more: https://aka.ms/cosmos-native-rbac.
ActivityId: xxx, Microsoft.Azure.Documents.Common/2.14.0
```
