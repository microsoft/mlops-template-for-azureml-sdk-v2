import requests
from requests.structures import CaseInsensitiveDict
import argparse
import os

def Invoke_Pipeline(
    pipeline_pat,
    env_selection,
    build_number,
    org_name,
    project_name,
    error_pipeline_definition_number,
    error_pipeline_version_number,
    azdo_pipeline_rest_version, 
    error_message, error_step 
    ):
    headers = CaseInsensitiveDict()
    basic_auth_credentials = ('', pipeline_pat)
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
            "env_selection": env_selection,
            "trigger_buildid": build_number,
            "error_message": error_message,
            "error_step": error_step
        }
    }

    url = "https://dev.azure.com/{}/{}/_apis/pipelines/{}/runs?pipelineVersion={}&api-version={}".format(
        org_name, 
        project_name, 
        error_pipeline_definition_number, 
        error_pipeline_version_number, 
        azdo_pipeline_rest_version
    )

    resp = requests.post(url, auth=basic_auth_credentials, headers=headers, json=request_body)
    print(f"response code {resp.status_code}")

    

if __name__ == "__main__":
    print("This should be called using main!")
    