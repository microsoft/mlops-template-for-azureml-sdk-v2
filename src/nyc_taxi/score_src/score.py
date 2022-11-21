import argparse
import pandas as pd
import os
from pathlib import Path
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
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


try:
    mlflow.sklearn.autolog()

    parser = argparse.ArgumentParser("score")
    parser.add_argument(
        "--predictions", type=str, help="Path of predictions and actual data"
    )
    parser.add_argument("--model", type=str, help="Path to model")
    parser.add_argument("--score_report", type=str, help="Path to score report")
    parser.add_argument("--org_name", type=str, help="Path to model")
    parser.add_argument("--project_name", type=str, help="Path to score report")
    parser.add_argument("--pipeline_pat", type=str, help="Path to model")
    parser.add_argument("--azdo_pipeline_rest_version", type=str, help="Path to score report")
    parser.add_argument("--error_pipeline_definition_number", type=str, help="Path to model")
    parser.add_argument("--error_pipeline_version_number", type=str, help="Path to score report")
    parser.add_argument("--env_selection", type=str, help="Environment type dev, test, prod etc")
    parser.add_argument("--build_number", type=str, help="Build number ")


    args = parser.parse_args()

    print("hello scoring world...")

    lines = [
        f"Model path: {args.model}",
        f"Predictions path: {args.predictions}",
        f"Scoring output path: {args.score_report}",
    ]

    for line in lines:
        print(line)

    print("mounted_path files: ")
    arr = os.listdir(args.predictions)

    print(arr)
    df_list = []
    for filename in arr:
        print("reading file: %s ..." % filename)
        with open(os.path.join(args.predictions, filename), "r") as handle:
            # print (handle.read())
            input_df = pd.read_csv((Path(args.predictions) / filename))
            df_list.append(input_df)

    test_data = df_list[0]

    # Load the model from input port
    model = mlflow.sklearn.load_model(args.model)

    # Print the results of scoring the predictions against actual values in the test data
    # The coefficients
    print("Coefficients: \n", model.coef_)

    actuals = test_data["actual_cost"]
    predictions = test_data["predicted_cost"]

    # The mean squared error
    print("Mean squared error: %.2f" % mean_squared_error(actuals, predictions))
    # The coefficient of determination: 1 is perfect prediction
    print("Coefficient of determination: %.2f" % r2_score(actuals, predictions))
    print("Model: ", model)

    score_data = { "mean_squared_error" : mean_squared_error(actuals, predictions), "r2_score" : r2_score(actuals, predictions) }
    json_object = json.dumps(score_data) 
    """
    with open(args.score_report, "w") as f:
        json.dump(score_data, f)

    """

    with open((Path(args.score_report) / "score.json"), "a") as f:
        json.dump(score_data, f)
except Exception as e:
    print(str(e))
    invokeapi.Invoke_Pipeline(args.pipeline_pat,args.env_selection,args.build_number,args.org_name, args.project_name, args.error_pipeline_definition_number, args.error_pipeline_version_number,args.azdo_pipeline_rest_version, str(e), "Score")
    raise

