```
az ad sp create-for-rbac --name $sp_name --role contributor --scopes /subscriptions/$subscription/resourceGroups/$resource_group --sdk-auth
```


