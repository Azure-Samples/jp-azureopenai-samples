resourceGroupName='rg-tak-internal'
accountName='cosmos-hdi6iz53e43ay'
az cosmosdb sql role definition list --account-name $accountName --resource-group $resourceGroupName
readOnlyRoleDefinitionId='/subscriptions/fcf6dedb-c06b-41f1-8344-1c008ca4b872/resourceGroups/rg-tak-internal/providers/Microsoft.DocumentDB/databaseAccounts/cosmos-hdi6iz53e43ay/sqlRoleDefinitions/00000000-0000-0000-0000-000000000001'
principalId='2dc8d697-3e6e-4f8b-b0d0-09a7601d6a20'
az cosmosdb sql role assignment create --account-name $accountName --resource-group $resourceGroupName --scope "/" --principal-id $principalId --role-definition-id $readOnlyRoleDefinitionId
