import argparse
from asyncore import write
from pathlib import Path
from uuid import uuid4
from datetime import datetime
import os
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
import pickle
import mlflow
import mlflow.pyfunc
import json


def main(training_data, test_data, model_output,model_metadata):
    print("Hello training world...")

    lines = [
        f"Training data path: {training_data}",
        f"Test data path: {test_data}",
        f"Model output path: {model_output}",
        f"Job metadata output path: {model_metadata}",
    ]

    for line in lines:
        print(line)

    print("mounted_path files: ")
    arr = os.listdir(training_data)
    print(arr)

    df_list = []
    for filename in arr:
        print("reading file: %s ..." % filename)
        with open(os.path.join(training_data, filename), "r") as handle:
            # print (handle.read())
            input_df = pd.read_csv((Path(training_data) / filename))
            df_list.append(input_df)

    train_data = df_list[0]
    print(train_data.columns)

    trainX, testX, trainy, testy = split(train_data)
    write_test_data(testX, testy)
    train_model(trainX, trainy, model_metadata)


def split(train_data):
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

    return trainX, testX, trainy, testy


def train_model(trainX, trainy, model_metadata):
    #mlflow.autolog()
    # Train a Linear Regression Model with the train set
    model = LinearRegression().fit(trainX, trainy)
    print(model.score(trainX, trainy))

    # Output the model and test data
    #pickle.dump(model, open((Path(args.model_output) / "model.sav"), "wb"))
    model_info = mlflow.sklearn.log_model(sk_model=model, artifact_path=model_output,registered_model_name="mymodel")


    #mlflow.lightgbm.save_model(full_model, model_path)

def write_test_data(testX, testy):
    # test_data = pd.DataFrame(testX, columns = )
    testX["cost"] = testy
    print(testX.shape)
    testX.to_csv((Path(args.test_data) / "test_data.csv"))


if __name__ == "__main__":
    parser = argparse.ArgumentParser("train")
    parser.add_argument("--training_data", type=str, help="Path to training data")
    parser.add_argument("--test_data", type=str, help="Path to test data")
    parser.add_argument("--model_output", type=str, help="Path of output model")
    parser.add_argument("--model_metadata", type=str, help="Path for storing job metadata")

    args = parser.parse_args()

    training_data = args.training_data
    test_data = args.test_data
    model_output = args.model_output
    model_metadata = args.model_metadata

    main(training_data, test_data, model_output,model_metadata)