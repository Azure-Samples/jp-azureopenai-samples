 #!/bin/sh

echo ""
echo "Loading azd .env file from current environment"
echo ""

while IFS='=' read -r key value; do
    value=$(echo "$value" | sed 's/^"//' | sed 's/"$//')
    export "$key=$value"
done <<EOF
$(azd env get-values)
EOF

roleId=$(az cosmosdb sql role definition create --account-name "$AZURE_COSMOSDB_ACCOUNT" --resource-group "$AZURE_COSMOSDB_RESOURCE_GROUP" --body ./scripts/cosmosreadwriterole.json --output tsv --query id)
az cosmosdb sql role assignment create --account-name "$AZURE_COSMOSDB_ACCOUNT" --resource-group "$AZURE_COSMOSDB_RESOURCE_GROUP" --scope / --principal-id "$BACKEND_IDENTITY_PRINCIPAL_ID" --role-definition-id $roleId
az cosmosdb sql role assignment create --account-name "$AZURE_COSMOSDB_ACCOUNT" --resource-group "$AZURE_COSMOSDB_RESOURCE_GROUP" --scope / --principal-id "$AZURE_PRINCIPAL_ID" --role-definition-id $roleId


echo 'Creating python virtual environment "scripts/.venv"'
python -m venv scripts/.venv

echo 'Installing dependencies from "requirements.txt" into virtual environment'
./scripts/.venv/bin/python -m pip install -r scripts/requirements.txt

echo 'Running "prepdocs.py"'
./scripts/.venv/bin/python ./scripts/prepdocs.py './data/*' --storageaccount "$AZURE_STORAGE_ACCOUNT" --container "$AZURE_STORAGE_CONTAINER" --searchservice "$AZURE_SEARCH_SERVICE" --index "$AZURE_SEARCH_INDEX" --formrecognizerservice "$AZURE_FORMRECOGNIZER_SERVICE" --tenantid "$AZURE_TENANT_ID" -v
