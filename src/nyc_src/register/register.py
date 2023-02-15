import mlflow
import argparse
import os
import json


def main(model_metadata, model_name, build_reference):
    try:
        run_file = open(args.model_metadata)
        model_metadata = json.load(run_file)
    except Exception as ex:
        print(ex)
        raise
    finally:
        run_file.close()
        run_uri = model_metadata["run_uri"]
    model_version = mlflow.register_model(run_uri, model_name)
    client = mlflow.MlflowClient()

    client.set_model_version_tag(
        name=model_name,
        version=model_version.version,
        key="build_id",
        value=build_reference
        )
    print(model_version)


if __name__ == "__main__":
    parser = argparse.ArgumentParser("register_model")
    parser.add_argument("--model_metadata", type=str, help="model metadata on Machine Learning Workspace")
    parser.add_argument("--model_name", type=str, help="model name to be registered")
    parser.add_argument("--build_reference", type=str, help="Original AzDo build id that initiated experiment")

    args = parser.parse_args()
    
    print(args.model_metadata)
    print(args.model_name)
    #print(args.trigger_buildid)

    main(args.model_metadata , args.model_name, args.build_reference )
