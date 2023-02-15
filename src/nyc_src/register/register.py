from azure.ai.ml import MLClient
from azure.ai.ml.entities import Model
from azure.identity import DefaultAzureCredential
from azure.ai.ml.constants import AssetTypes
import argparse
import os
import json


def main(model_path, model_name,subscription_id,resource_group_name,workspace_name):
        # , trigger_buildid
    client = MLClient(
        DefaultAzureCredential(),
        subscription_id=subscription_id,
        resource_group_name=resource_group_name,
        workspace_name=workspace_name,
    )
    try:
        credential = DefaultAzureCredential()
        credential.get_token("https://management.azure.com/.default")
    except Exception as ex:
        raise

    try:
        run_model = Model(
            path=model_path + "/model.sav",
            name=model_name,
            description="Model creation from experiment.",
            type=AssetTypes.CUSTOM_MODEL,
            properties={
                "accuracy": "aa",
            },
        )

        client.models.create_or_update(run_model)
    except Exception as ex:
        raise


if __name__ == "__main__":

    parser = argparse.ArgumentParser("register_model")
    parser.add_argument("--model_path", type=str, help="model path on Machine Learning Workspace")
    parser.add_argument("--model_name", type=str, help="model name to be registered")
    parser.add_argument("--subscription_id", type=str, help="Azure subscription id")
    parser.add_argument("--resource_group_name", type=str, help="Azure Machine learning resource group")
    parser.add_argument("--workspace_name", type=str, help="Azure Machine learning Workspace name")
   # parser.add_argument("--trigger_buildid", type=str, help="Original AzDo build id that initiated experiment")


    args = parser.parse_args()
    
    print(args.model_path)
    print(args.model_name)
    #print(args.trigger_buildid)

    main(args.model_path , args.model_name, args.subscription_id, args.resource_group_name, args.workspace_name )
