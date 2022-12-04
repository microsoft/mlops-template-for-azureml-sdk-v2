

from azure.ai.ml import MLClient
from azure.ai.ml.entities import Model
from azure.identity import DefaultAzureCredential
from azure.ai.ml.constants import AssetTypes
import mlflow
import argparse


parser = argparse.ArgumentParser("register_model")
parser.add_argument("--subscription_id", type=str, help="Azure subscription id")
parser.add_argument("--resource_group_name", type=str, help="Azure Machine learning resource group")
parser.add_argument("--workspace_name", type=str, help="Azure Machine learning Workspace name")
parser.add_argument("--model_run_path", type=str, help="model path on Machine Learning Workspace")
parser.add_argument("--model_name", type=str, help="model name to be registered")
parser.add_argument("--mean_squared_error", type=str, help="Mean Squared Error Metric of the new model based on training")
parser.add_argument("--r2_score", type=str, help="R2 score of the new model based on training")
parser.add_argument("--trigger_buildid", type=str, help="Original AzDo build id that initiated experiment")

args = parser.parse_args()
client = MLClient(DefaultAzureCredential(),subscription_id=args.subscription_id,
    resource_group_name=args.resource_group_name,
    workspace_name=args.workspace_name)

azureml_mlflow_uri = client.workspaces.get(args.workspace_name).mlflow_tracking_uri
mlflow.set_tracking_uri(azureml_mlflow_uri)
try:
    credential = DefaultAzureCredential()
    credential.get_token("https://management.azure.com/.default")
except Exception as ex:
   print("Oops! Invalid credentials.. Try again...")
   raise

from azure.ai.ml.entities import Model
from azure.ai.ml.constants import AssetTypes

run_model = Model(
    path=args.model_run_path,
    name=args.model_name,
    description="Model creation from experiment.",
    type=AssetTypes.MLFLOW_MODEL,properties={ "mean_squared_error": args.mean_squared_error, 
        "r2_score": args.r2_score, 
        "trigger_buildid": args.trigger_buildid }
    
)

client.models.create_or_update(run_model)