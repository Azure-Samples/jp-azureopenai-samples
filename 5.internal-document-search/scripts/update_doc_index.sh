export RESOURSE_GROUP=
export AZURE_STORAGE_ACCOUNT=
export AZURE_STORAGE_CONTAINER=
export AZURE_STORAGE_KEY=$(az storage account keys list -g "$RESOURSE_GROUP" -n "$AZURE_STORAGE_ACCOUNT" | grep -Po '"value": "\K[^"]*' | head -n1)
export AZURE_SEARCH_SERVICE=
export AZURE_SEARCH_INDEX=
export AZURE_FORMRECOGNIZER_SERVICE=
export AZURE_TENANT_ID=

echo 'Creating python virtual environment "scripts/.venv"'
python -m venv scripts/.venv
# If the above command fails, try python3
if [ $? -eq 127 ]; then
    python3 -m venv scripts/.venv
fi

echo 'Installing dependencies from "requirements.txt" into virtual environment'
./scripts/.venv/bin/python -m pip install -r scripts/requirements.txt

./scripts/.venv/bin/python ./scripts/prepdocs.py './data/*' --storageaccount "$AZURE_STORAGE_ACCOUNT" --container "$AZURE_STORAGE_CONTAINER" --storagekey "$AZURE_STORAGE_KEY" --searchservice "$AZURE_SEARCH_SERVICE" --index "$AZURE_SEARCH_INDEX" --formrecognizerservice "$AZURE_FORMRECOGNIZER_SERVICE" --tenantid "$AZURE_TENANT_ID" -v
