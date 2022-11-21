

from azure.ai.ml import MLClient
from azure.identity import DefaultAzureCredential
import mlflow
import argparse
from azure.ai.ml.entities import ComputeInstance, AmlCompute


parser = argparse.ArgumentParser("prepare_compute")
parser.add_argument("--subscription_id", type=str, help="Azure subscription id")
parser.add_argument("--resource_group_name", type=str, help="Azure Machine learning resource group")
parser.add_argument("--workspace_name", type=str, help="Azure Machine learning Workspace name")
parser.add_argument("--cluster_name", type=str, help="Azure Machine learning cluster name")
parser.add_argument("--cluster_size", type=str, help="Azure Machine learning cluster size")
parser.add_argument("--cluster_region", type=str, help="Azure Machine learning cluster region")


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
    try:
        compute_object = client.compute.get(args.cluster_name)   
    except:
        compute_object = AmlCompute(
            name=args.cluster_name,
            type="amlcompute",
            size=args.cluster_size,
            location=args.cluster_region,
            min_instances=0,
            max_instances=1,
            idle_time_before_scale_down=120,
        )
        compute_object = client.compute.begin_create_or_update(compute_object).result()
except Exception as ex:
   print("Oops!  invalid credentials.. Try again...")
   raise


