$env:RESOURSE_GROUP=
$env:AZURE_STORAGE_ACCOUNT=
$env:AZURE_STORAGE_CONTAINER=
$env:AZURE_STORAGE_KEY=(az storage account keys list -g $env:RESOURSE_GROUP -n $env:AZURE_STORAGE_ACCOUNT | ConvertFrom-Json)[0].value
$env:AZURE_SEARCH_SERVICE=
$env:AZURE_SEARCH_INDEX=
$env:AZURE_FORMRECOGNIZER_SERVICE=
$env:AZURE_TENANT_ID=

$pythonCmd = Get-Command python -ErrorAction SilentlyContinue
if (-not $pythonCmd) {
  # fallback to python3 if python not found
  $pythonCmd = Get-Command python3 -ErrorAction SilentlyContinue
}

Write-Host 'Creating python virtual environment "scripts/.venv"'
Start-Process -FilePath ($pythonCmd).Source -ArgumentList "-m venv ./scripts/.venv" -Wait -NoNewWindow

$venvPythonPath = "./scripts/.venv/scripts/python.exe"
if (Test-Path -Path "/usr") {
  # fallback to Linux venv path
  $venvPythonPath = "./scripts/.venv/bin/python"
}

Write-Host 'Installing dependencies from "requirements.txt" into virtual environment'
Start-Process -FilePath $venvPythonPath -ArgumentList "-m pip install -r ./scripts/requirements.txt" -Wait -NoNewWindow

Write-Host 'Running "prepdocs.py"'
$cwd = (Get-Location)

if ($cloudshell) {
  Write-Host "Assume managed identity credential of Azure Cloud Shell" # TODO: Delete before PR
  Start-Process -FilePath $venvPythonPath -ArgumentList "./scripts/prepdocs.py $cwd/data/* --storageaccount $env:AZURE_STORAGE_ACCOUNT --container $env:AZURE_STORAGE_CONTAINER --searchservice $env:AZURE_SEARCH_SERVICE --searchkey $env:AZURE_SEARCH_KEY --index $env:AZURE_SEARCH_INDEX --formrecognizerservice $env:AZURE_FORMRECOGNIZER_SERVICE --formrecognizerkey $env:AZURE_FORMRECOGNIZER_KEY --tenantid $env:AZURE_TENANT_ID --storagekey $env:AZURE_STORAGE_KEY -v --managedidentitycredential" -Wait -NoNewWindow
} else {
  Write-Host "Assume azd credential" # TODO: Delete before PR
  Start-Process -FilePath $venvPythonPath -ArgumentList "./scripts/prepdocs.py $cwd/data/* --storageaccount $env:AZURE_STORAGE_ACCOUNT --container $env:AZURE_STORAGE_CONTAINER --searchservice $env:AZURE_SEARCH_SERVICE --index $env:AZURE_SEARCH_INDEX --formrecognizerservice $env:AZURE_FORMRECOGNIZER_SERVICE --tenantid $env:AZURE_TENANT_ID -v" -Wait -NoNewWindow
}
