
import mlflow
import argparse
import os
import json


def main(model_metadata, model_name):
        # , trigger_buildid
    try:
        run_file = open(args.model_metadata)
        model_metadata = json.load(run_file)
    except Exception as ex:
        print(ex)
        raise
    finally:
        run_file.close()
        run_uri = model_metadata["run_uri"]
    model_version = mlflow.register_model(run_uri, model_name,tags={"buildid" : "100"})
    print(model_version)

if __name__ == "__main__":

    parser = argparse.ArgumentParser("register_model")
    parser.add_argument("--model_metadata", type=str, help="model path on Machine Learning Workspace")
    parser.add_argument("--model_name", type=str, help="model name to be registered")
   # parser.add_argument("--trigger_buildid", type=str, help="Original AzDo build id that initiated experiment")


    args = parser.parse_args()
    
    print(args.model_metadata)
    print(args.model_name)
    #print(args.trigger_buildid)

    main(args.model_metadata , args.model_name )
