from azure.identity import DefaultAzureCredential
import argparse
from azure.ai.ml.dsl import pipeline
from azure.ai.ml import MLClient, Input, Output, command
from azure.ai.ml import load_component
import time
import os


parser = argparse.ArgumentParser("build_environment")
parser.add_argument("--subscription_id", type=str, help="Azure subscription id")
parser.add_argument("--resource_group_name", type=str, help="Azure Machine learning resource group")
parser.add_argument("--workspace_name", type=str, help="Azure Machine learning Workspace name")
parser.add_argument("--cluster_name", type=str, help="Azure Machine learning cluster name")
parser.add_argument("--build_reference", type=str, help="Unique identifier for Azure DevOps pipeline run")
parser.add_argument("--deploy_environment", type=str, help="execution and deployment environment. e.g. dev, prod, test")
parser.add_argument("--experiment_name", type=str, help="Job execution experiment name")
parser.add_argument("--ml_pipeline_name", type=str, help="name of pipeline")
parser.add_argument("--wait_for_completion", type=str, help="determine if pipeline to wait for job completion")
parser.add_argument("--pipeline_pat", type=str, help="pat for calling Azure DevOps Rest API authentication")
parser.add_argument("--azdo_pipeline_rest_version", type=str, help="Azure DevOps Rest API version to use for callback")
parser.add_argument("--project_name", type=str, help="The name of the Azure DevOps project used for callback")
parser.add_argument("--org_name", type=str, help="The name of the Azure DevOps Organization used for callback")
parser.add_argument("--register_pipeline_version_number", type=str, help="Azure DevOps pipeline version to use for callback")
parser.add_argument("--register_pipeline_definition_number", type=str, help="Azure DevOps pipeline definition number to use for callback")
parser.add_argument("--environment_name", type=str, help="Azure Machine Learning Environment name for job execution")

args = parser.parse_args()

try:
    client = MLClient(DefaultAzureCredential(),
        subscription_id=args.subscription_id,
        resource_group_name=args.resource_group_name,
        workspace_name=args.workspace_name)
except Exception as ex:
   print("Oops!  invalid credentials.. Try again...")
   raise

parent_dir = os.path.join(os.getcwd(), "mlops/nyc_taxi/components")
data_dir = os.path.join(os.getcwd(), "mlops/nyc-taxi/data/")

prepare_data = load_component(source=parent_dir + "/prep.yml")
transform_data = load_component(source=parent_dir + "/transform.yml")
train_model = load_component(source=parent_dir + "/train.yml")
predict_result = load_component(source=parent_dir + "/predict.yml")
score_data = load_component(source=parent_dir + "/score.yml")

# Set the environment name to custom environment using name and version number
prepare_data.environment = f"azureml:{args.environment_name}:{args.build_reference}"
transform_data.environment = f"azureml:{args.environment_name}:{args.build_reference}"
train_model.environment = f"azureml:{args.environment_name}:{args.build_reference}"
predict_result.environment = f"azureml:{args.environment_name}:{args.build_reference}"
score_data.environment = f"azureml:{args.environment_name}:{args.build_reference}"

if args.wait_for_completion == "False":
    callback_pipeline = command(
        name="callback-azdo-pipeline",
        display_name="Callback Azure DevOps pipeline to register model",
        description="Callback Azure DevOps pipeline to register model",
        command ="""python mlops/nyc-taxi/src/azdo_pipeline_callback.py 
            --modelpath ${{inputs.model_path}} 
            --model_folder ${{inputs.model_folder}} 
            --score_path ${{inputs.score_path}} 
            --buildid ${{inputs.buildid}} 
            --pipeline_pat ${{inputs.pipeline_pat}} 
            --azdo_pipeline_rest_version ${{inputs.azdo_pipeline_rest_version}} 
            --project_name ${{inputs.project_name}} 
            --org_name ${{inputs.org_name}} 
            --register_pipeline_version_number ${{inputs.register_pipeline_version_number}} 
            --register_pipeline_definition_number ${{inputs.register_pipeline_definition_number}}""",
        environment=f"azureml:{args.environment_name}:{args.build_reference}",
        inputs=dict(final_output=Input(type="uri_folder"), model_path=Input(type="uri_file"), model_folder=Input(type="mlflow_model"), score_path=Input(type="uri_folder"), buildid=args.build_reference, pipeline_pat=args.pipeline_pat, azdo_pipeline_rest_version=args.azdo_pipeline_rest_version, project_name=args.project_name, org_name=args.org_name, register_pipeline_version_number=args.register_pipeline_version_number, register_pipeline_definition_number=args.register_pipeline_definition_number ),
        outputs=dict(output_folder=Output(type="uri_folder", mode="rw_mount")),
        code="."
    )

@pipeline(name=args.ml_pipeline_name,
    display_name=args.ml_pipeline_name, 
    experiment_name=args.experiment_name, 
    tags={
        'environment': args.deploy_environment,
        'build_reference': args.build_reference 
    })
def nyc_taxi_data_regression(pipeline_job_input):
    prepare_sample_data = prepare_data(
        raw_data=pipeline_job_input,
        )
    transform_sample_data = transform_data(
        clean_data=prepare_sample_data.outputs.prep_data,
    )
    train_with_sample_data = train_model(
        training_data=transform_sample_data.outputs.transformed_data,
    )
    predict_with_sample_data = predict_result(
        model_input=train_with_sample_data.outputs.model_output,
        test_data=train_with_sample_data.outputs.test_data,
    )
    score_with_sample_data = score_data(
        predictions=predict_with_sample_data.outputs.predictions,
        model=train_with_sample_data.outputs.model_output,
    )
    if args.wait_for_completion == "False":
        callback_pipeline_with_data = callback_pipeline(
            final_output=score_with_sample_data.outputs.score_report,
            model_folder=train_with_sample_data.outputs.model_output,
            model_path=train_with_sample_data.outputs.model_perf_data,
            score_path = score_with_sample_data.outputs.score_report
    )
    return {
        "pipeline_job_prepped_data": prepare_sample_data.outputs.prep_data,
        "pipeline_job_transformed_data": transform_sample_data.outputs.transformed_data,
        "pipeline_job_trained_model": train_with_sample_data.outputs.model_output,
        "pipeline_job_test_data": train_with_sample_data.outputs.test_data,
        "pipeline_job_predictions": predict_with_sample_data.outputs.predictions,
        "pipeline_job_score_report": score_with_sample_data.outputs.score_report
    }


pipeline_job = nyc_taxi_data_regression(
    Input(type="uri_folder", path=data_dir), 
)

# demo how to change pipeline output settings
pipeline_job.outputs.pipeline_job_prepped_data.mode = "rw_mount"

# set pipeline level compute
pipeline_job.settings.default_compute = args.cluster_name

# set pipeline level datastore
pipeline_job.settings.default_datastore = "workspaceblobstore"

# Submit pipeline job to workspace
pipeline_job = client.jobs.create_or_update(
    pipeline_job, experiment_name=args.experiment_name 
)

if pipeline_job == None:
    print("Job creation failed")
    raise

current_job = client.jobs.get(pipeline_job.name)
if current_job == None:
    print("no job found with given name")
    raise

if args.wait_for_completion == "True":
    total_wait_time = 1800
    current_wait_time = 0
    job_status = ["NotStarted", "Queued", "Starting", "Preparing", "Running", "Finalizing"]
    while current_job.status in job_status:
        if current_wait_time <= total_wait_time:
            time.sleep(15)
            current_job = client.jobs.get(pipeline_job.name) 
            print(current_job.status)
            current_wait_time += current_wait_time + 15
        else:
            break
    print(current_job.status)
    if current_job.status == 'Completed' or current_job.status == 'Finished':
        print(f"job status: {current_job.status}")
        print("exiting job successfully..")
    else:
        print("exiting job with failure..")
     







