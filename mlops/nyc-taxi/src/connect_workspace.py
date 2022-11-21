

from azure.ai.ml import MLClient
from azure.identity import DefaultAzureCredential
import mlflow
import argparse



parser = argparse.ArgumentParser("connect_workspace")
parser.add_argument("--subscription_id", type=str, help="Azure subscription id")
parser.add_argument("--resource_group_name", type=str, help="Azure Machine learning resource group")
parser.add_argument("--workspace_name", type=str, help="Azure Machine learning Workspace name")

args = parser.parse_args()
client = MLClient(DefaultAzureCredential(),
    subscription_id=args.subscription_id,
    resource_group_name=args.resource_group_name,
    workspace_name=args.workspace_name)

azureml_mlflow_uri = client.workspaces.get(args.workspace_name).mlflow_tracking_uri
mlflow.set_tracking_uri(azureml_mlflow_uri)
try:
    credential = DefaultAzureCredential()
    credential.get_token("https://management.azure.com/.default")
except Exception as ex:
   print("Oops!  invalid credentials.. Try again...")
   raise