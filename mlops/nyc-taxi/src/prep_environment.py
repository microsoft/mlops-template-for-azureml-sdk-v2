

from azure.ai.ml import MLClient
from azure.identity import DefaultAzureCredential
import mlflow
import argparse

from azure.ai.ml.entities import Environment


parser = argparse.ArgumentParser("prepare_environment")
parser.add_argument("--subscription_id", type=str, help="Azure subscription id")
parser.add_argument("--resource_group_name", type=str, help="Azure Machine learning resource group")
parser.add_argument("--workspace_name", type=str, help="Azure Machine learning Workspace name")
parser.add_argument("--env_base_image_name", type=str, help="Environment custom base image name")
parser.add_argument("--conda_path", type=str, help="path to conda requirements file")
parser.add_argument("--environment_name", type=str, help="Azure Machine learning environment name")
parser.add_argument("--version_number", type=str, help="Azure Machine learning environment version number")

args = parser.parse_args()
client = MLClient(DefaultAzureCredential(),subscription_id=args.subscription_id,
    resource_group_name=args.resource_group_name,
    workspace_name=args.workspace_name)

azureml_mlflow_uri = client.workspaces.get(args.workspace_name).mlflow_tracking_uri
mlflow.set_tracking_uri(azureml_mlflow_uri)

print(args.environment_name)
print("done")

try:
    credential = DefaultAzureCredential()
    credential.get_token("https://management.azure.com/.default")
    env_docker_conda = Environment(
        image=args.env_base_image_name,
        conda_file=args.conda_path,
        name=args.environment_name,
        description="Environment created using Conda.", 
        version=args.version_number
    )
    client.environments.create_or_update(env_docker_conda)
    
except Exception as ex:
   print("Oops! invalid credentials or error while creating ML environment.. Try again...")
   raise