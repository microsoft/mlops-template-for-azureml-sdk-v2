import argparse
from pathlib import Path
from uuid import uuid4
from datetime import datetime
import os
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
import mlflow
import json
import pathlib
import sys
import site
from importlib import reload

SCRIPT_DIR = f"{os.getcwd()}/nyc_taxi"
sys.path.append(str(SCRIPT_DIR))
reload(site)
from  azdorestapi import invokeapi

#mlflow.sklearn.autolog()
try:
    parser = argparse.ArgumentParser("train")
    parser.add_argument("--training_data", type=str, help="Path to training data")
    parser.add_argument("--test_data", type=str, help="Path to test data")
    parser.add_argument("--model_output", type=str, help="Path of output model")
    parser.add_argument("--model_perf_data", type=str, help="file for storing model performance metrics")
    parser.add_argument("--org_name", type=str, help="Path to model")
    parser.add_argument("--project_name", type=str, help="Path to score report")
    parser.add_argument("--pipeline_pat", type=str, help="Path to model")
    parser.add_argument("--azdo_pipeline_rest_version", type=str, help="Path to score report")
    parser.add_argument("--error_pipeline_definition_number", type=str, help="Path to model")
    parser.add_argument("--error_pipeline_version_number", type=str, help="Path to score report")
    parser.add_argument("--env_selection", type=str, help="Environment type dev, test, prod etc")
    parser.add_argument("--build_number", type=str, help="Build number ")

    args = parser.parse_args()

    print("hello training world...")

    lines = [
        f"Training data path: {args.training_data}",
        f"Test data path: {args.test_data}",
        f"Model output path: {args.model_output}",
    ]

    for line in lines:
        print(line)

    print("mounted_path files: ")
    arr = os.listdir(args.training_data)
    print(arr)

    df_list = []
    for filename in arr:
        print("reading file: %s ..." % filename)
        with open(os.path.join(args.training_data, filename), "r") as handle:
            # print (handle.read())
            input_df = pd.read_csv((Path(args.training_data) / filename))
            df_list.append(input_df)

    train_data = df_list[0]
    print(train_data.columns)

    # Split the data into input(X) and output(y)
    y = train_data["cost"]
    # X = train_data.drop(['cost'], axis=1)
    X = train_data[
        [
            "distance",
            "dropoff_latitude",
            "dropoff_longitude",
            "passengers",
            "pickup_latitude",
            "pickup_longitude",
            "store_forward",
            "vendor",
            "pickup_weekday",
            "pickup_month",
            "pickup_monthday",
            "pickup_hour",
            "pickup_minute",
            "pickup_second",
            "dropoff_weekday",
            "dropoff_month",
            "dropoff_monthday",
            "dropoff_hour",
            "dropoff_minute",
            "dropoff_second",
        ]
    ]

    # Split the data into train and test sets
    trainX, testX, trainy, testy = train_test_split(X, y, test_size=0.3, random_state=42)
    print(trainX.shape)
    print(trainX.columns)

    # Train a Linear Regression Model with the train set
    model = LinearRegression().fit(trainX, trainy)
    print(model.score(trainX, trainy))
    modelinf = mlflow.sklearn.log_model(model,"model_folder")

    model_data = { "run_id" : modelinf.run_id, "run_uri" : modelinf.model_uri }
    json_object = json.dumps(model_data) 
    with open(args.model_perf_data, "w") as f:
        json.dump(model_data, f)



    mlflow.sklearn.save_model(model, args.model_output)

    modelinf.model_uri
    # test_data = pd.DataFrame(testX, columns = )
    testX["cost"] = testy
    print(testX.shape)
    test_data = testX.to_csv(Path(args.test_data) / "test_data.csv")
except Exception as e:
    print(str(e))
    invokeapi.Invoke_Pipeline(args.pipeline_pat,args.env_selection,args.build_number,args.org_name, args.project_name, args.error_pipeline_definition_number, args.error_pipeline_version_number,args.azdo_pipeline_rest_version, str(e), "train")
    raise