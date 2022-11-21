import requests
from requests.structures import CaseInsensitiveDict
import argparse
import json
from pathlib import Path


parser = argparse.ArgumentParser()
parser.add_argument("--modelpath", required=True, type=str, help="Path to input model")
parser.add_argument("--score_path", required=True, type=str, help="Path to input model")
parser.add_argument("--buildid", required=True, type=str, help="Path to input model")
parser.add_argument("--pipeline_pat", required=True, type=str, help="PAT for Azure DevOps Rest API authentication")
parser.add_argument("--azdo_pipeline_rest_version", type=str, help="Azure DevOps Rest API version to use for callback")
parser.add_argument("--project_name", type=str, help="The name of the Azure DevOps project used for callback")
parser.add_argument("--model_folder", required=True, type=str, help="Path to input model")
parser.add_argument("--org_name", type=str, help="The name of the Azure DevOps Organization used for callback")
parser.add_argument("--register_pipeline_version_number", type=str, help="Azure DevOps pipeline version to use for callback")
parser.add_argument("--register_pipeline_definition_number", type=str, help="Azure DevOps pipeline definition number to use for callback")


args = parser.parse_args()
modelpath = args.modelpath

f = open(modelpath)
data = json.load(f)
f.close()

run_id = data["run_id"]
run_uri = data["run_uri"]

f = open((Path(args.score_path) / "score.json"))
data = json.load(f)
f.close()
r2_score = data["r2_score"]
mean_squared_error = data["mean_squared_error"]

headers = CaseInsensitiveDict()
basic_auth_credentials = ('', args.pipeline_pat)
headers["Content-Type"] = "application/json"

request_body = {
    "resources": {
        "repositories": {
            "main": {
                "refName": "refs/heads/main"
            }
        }
    },
    "templateParameters": {
        "envSelection": "dev",
        "runid": run_id,
        "runuri": run_uri,
        "r2_score": r2_score,
        "mean_squared_error": mean_squared_error,
        "trigger_buildid": args.buildid
    }
}

url = "https://dev.azure.com/{}/{}/_apis/pipelines/{}/runs?pipelineVersion={}&api-version={}".format(
    args.org_name, 
    args.project_name, 
    args.register_pipeline_definition_number, 
    args.register_pipeline_version_number, 
    args.azdo_pipeline_rest_version
)

resp = requests.post(url, auth=basic_auth_credentials, headers=headers, json=request_body)
print(f"response code {resp.status_code}")

