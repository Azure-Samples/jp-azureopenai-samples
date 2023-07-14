# Log Analytics
## Step 1: Create an Azure Log Analytics workspace
### Create a resource group (if needed)
```
az group create --name $RG --location $LOC
```
### Create a Log Analytics workspace
```
az monitor log-analytics workspace create --resource-group $RG --workspace-name $WSNAME --location $LOC
```
### Retrieve the workspace ID and key
```
az monitor log-analytics workspace get-shared-keys --resource-group $RG --workspace-name $WSNAME
```
## Step 2: Enable Diagnostics Logging on App Service
https://learn.microsoft.com/en-us/azure/app-service/troubleshoot-diagnostic-logs

## Step 3: Check logs in Log Analytics
```
AppServiceConsoleLogs
```
```
AppServiceHTTPLogs
```

# Application Insights (Untested very rough draft)
# Step 1: Create an Application Insights resource
## From the Portal
In the Azure portal, click on "Create a resource" and search for "Application Insights".
Click on "Application Insights" from the search results.
Click on "Create" to start creating a new Application Insights resource.
Provide the required details such as subscription, resource group, instance name, and region.
Configure other optional settings as per your requirements.
In the "Instrumentation Key" section, select "Create new" and choose the Log Analytics workspace you created in Step 1.
Click on "Review + Create" and then click on "Create" to create the Application Insights resource.
## With the Azure CLI
### Create an Application Insights resource
`az monitor app-insights component create --app $APPI --resource-group $RG --location $LOC`
### Retrieve the instrumentation key
`az monitor app-insights component show --app $APPI --resource-group $RG --query 'instrumentationKey' --output tsv`

# Step 2: Install the necessary packages:
Open a terminal or command prompt.
Navigate to your Flask application directory.
Run the following command to install the applicationinsights package:
```
pip install applicationinsights
```
WARNINING: The OpenTelemetry library might be preferrable

# Step 3: Instrument your Flask application with Application Insights:
Import the necessary modules in your Flask application file (app.py or similar):
```python
from applicationinsights import TelemetryClient
from applicationinsights.flask.ext import AppInsights
Initialize the Application Insights instrumentation by adding the following code before creating your Flask app instance:
```
```python
instrumentation_key = "<your_instrumentation_key>"
appinsights = AppInsights(app, instrumentation_key=instrumentation_key)
```
Replace <your_instrumentation_key> with the instrumentation key of your Application Insights resource.

WARNINING: The OpenTelemetry library might be preferrable

# Step 4: Configure logging in your Flask application:
Import the necessary module at the top of your Flask application file:
```python
import logging
``
Add the following code to configure the Flask app to use the Application Insights logger:
```python
app.logger.addHandler(appinsights.get_logger_handler())
``
Optionally, you can set the logging level to capture logs of a specific severity, such as errors and warnings:
```python
app.logger.setLevel(logging.WARNING)
```

# Step 5: Start your Flask application:

Run your Flask application as you normally would.

# Step 6: View logs in Application Insights and Log Analytics

Once your application is sending logs to Application Insights, you can view them by navigating to your Application Insights resource in the Azure portal.
In the Application Insights resource, you can explore different sections like "Logs," "Metrics," "Failures," and "Performance" to analyze the logs and monitor your application's behavior.
To access the logs in Log Analytics, go to your Log Analytics workspace in the Azure portal.
In the Log Analytics workspace, you can create custom queries to search and analyze the logs based on specific criteria.
Use the powerful querying capabilities of Log Analytics to filter and aggregate the logs, set up alerts, and create visualizations or dashboards as per your monitoring needs.
By following these steps, you'll be able to set up Application Insights and Log Analytics for monitoring error and warning logs from your application.
