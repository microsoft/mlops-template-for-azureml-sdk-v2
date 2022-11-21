

from azure.ai.ml import MLClient
from azure.ai.ml.entities import Model
from azure.identity import DefaultAzureCredential
import mlflow
import argparse



parser = argparse.ArgumentParser("compare_models")
parser.add_argument("--subscription_id", type=str, help="Azure subscription id")
parser.add_argument("--resource_group_name", type=str, help="Azure Machine learning resource group")
parser.add_argument("--workspace_name", type=str, help="Azure Machine learning Workspace name")
parser.add_argument("--model_name", type=str, help="model name to be registered")
parser.add_argument("--mean_squared_error", type=str, help="Mean Squared error metric for comparison")
parser.add_argument("--r2_score", type=str, help="R2 Score metric for comparison")

args = parser.parse_args()
client = MLClient(DefaultAzureCredential(),subscription_id=args.subscription_id,resource_group_name=args.resource_group_name,workspace_name=args.workspace_name)

azureml_mlflow_uri = client.workspaces.get(args.workspace_name).mlflow_tracking_uri
mlflow.set_tracking_uri(azureml_mlflow_uri)
try:
    credential = DefaultAzureCredential()
    credential.get_token("https://management.azure.com/.default")
except Exception as ex:
   print("Oops! invalid credentials..  Try again...")
   raise

versions = []
try:
    for i in client.models.list(args.model_name):
        print(i.version)
        versions.append(int(i.version))
except Exception as e:
     print("there are no prior model with this name. The new model can be registered after approval")

else:
    if (len(versions) > 0):
        versions.sort(reverse=True)
        print(versions[0])
        current_model = client.models.get(args.model_name,version=versions[0])

        if "mean_squared_error" in current_model.properties and "r2_score" in current_model.properties:
            print(current_model.properties["mean_squared_error"])
            print(current_model.properties["r2_score"])

            if (args.r2_score > current_model.properties["r2_score"]):
                print("r2_score is better in new model")
                print("r2_score is NOT better in existing model")
                
            else:
                print("r2_score is NOT better in new model")
                print("r2_score is better in existing model")
            print(f"Existing model r2_score = {current_model.properties['r2_score']} and new model r2_score = {args.r2_score}")

            if (args.mean_squared_error > current_model.properties["mean_squared_error"]):
                print("mean_squared_error is better in new model")
                print("mean_squared_error is NOT better in existing model")
                
            else:
                print("mean_squared_error is NOT better in new model")
                print("mean_squared_error is better in existing model")
            print(f"Existing model mean_squared_error = {current_model.properties['mean_squared_error']} and new model mean_squared_error = {args.mean_squared_error}")
        else:
            print("the model scores are not matching")
    else:
        print("there are no prior model with this name. The new model can be registered after approval")




