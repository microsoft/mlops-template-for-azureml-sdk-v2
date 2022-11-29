from azure.identity import DefaultAzureCredential
import argparse
from azure.ai.ml.dsl import pipeline
from azure.ai.ml import MLClient, Input
from azure.ai.ml import load_component
import time
import os
from mlops.common import get_compute, get_environment


ml_pipeline_name = ""
display_name = ""
experiment_name = ""
deploy_environment = ""
build_reference = ""

@pipeline(name=ml_pipeline_name,
    display_name=display_name, 
    experiment_name=experiment_name, 
    tags={
        'environment': deploy_environment,
        'build_reference': build_reference 
    })
def nyc_taxi_data_regression(
    pipeline_job_input,
    prepare_data,
    transform_data,
    train_model,
    predict_result,
    score_data
):
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
    return {
        "pipeline_job_prepped_data": prepare_sample_data.outputs.prep_data,
        "pipeline_job_transformed_data": transform_sample_data.outputs.transformed_data,
        "pipeline_job_trained_model": train_with_sample_data.outputs.model_output,
        "pipeline_job_test_data": train_with_sample_data.outputs.test_data,
        "pipeline_job_predictions": predict_with_sample_data.outputs.predictions,
        "pipeline_job_score_report": score_with_sample_data.outputs.score_report
    }

def construct_pipeline(
    cluster_name: str,
    environment_name: str
):
    parent_dir = os.path.join(os.getcwd(), "mlops/nyc-taxi/components")
    data_dir = os.path.join(os.getcwd(), "mlops/nyc-taxi/data/")

    prepare_data = load_component(source=parent_dir + "/prep.yml")
    transform_data = load_component(source=parent_dir + "/transform.yml")
    train_model = load_component(source=parent_dir + "/train.yml")
    predict_result = load_component(source=parent_dir + "/predict.yml")
    score_data = load_component(source=parent_dir + "/score.yml")

    # Set the environment name to custom environment using name and version number
    prepare_data.environment = environment_name
    transform_data.environment = environment_name
    train_model.environment = environment_name
    predict_result.environment = environment_name
    score_data.environment = environment_name

    pipeline_job = nyc_taxi_data_regression(
        Input(type="uri_folder", path=data_dir),
        prepare_data,
        transform_data,
        train_model,
        predict_result,
        score_data
    )

    # demo how to change pipeline output settings
    pipeline_job.outputs.pipeline_job_prepped_data.mode = "rw_mount"

    # set pipeline level compute
    pipeline_job.settings.default_compute = cluster_name

    # set pipeline level datastore
    pipeline_job.settings.default_datastore = "workspaceblobstore"

    return pipeline_job

def execute_pipeline(
    subscription_id: str,
    resource_group_name: str,
    workspace_name: str,
    experiment_name: str,
    pipeline_job: pipeline,
    wait_for_completion: str
):
    try:
        client = MLClient(
            DefaultAzureCredential(),
            subscription_id=subscription_id,
            resource_group_name=resource_group_name,
            workspace_name=workspace_name)

        pipeline_job = client.jobs.create_or_update(
            pipeline_job, experiment_name=experiment_name 
        )
    
        if wait_for_completion == "True":
            job_status = ["NotStarted", "Queued", "Starting", "Preparing", "Running", "Finalizing"]
            while pipeline_job.status in job_status:
                time.sleep(15)
                pipeline_job = client.jobs.get(pipeline_job.name) 
                print(pipeline_job.status)
        if pipeline_job.status == 'Completed' or pipeline_job.status == 'Finished':
            print(f"job status: {pipeline_job.status}")
            print("exiting job successfully..")
        else:
            print("exiting job with failure..")
    except Exception as ex:
        print("Oops! invalid credentials or error while creating ML environment.. Try again...")
        raise


def main():
    parser = argparse.ArgumentParser("build_environment")
    parser.add_argument("--subscription_id", type=str, help="Azure subscription id")
    parser.add_argument("--resource_group_name", type=str, help="Azure Machine learning resource group")
    parser.add_argument("--workspace_name", type=str, help="Azure Machine learning Workspace name")
    parser.add_argument("--cluster_name", type=str, help="Azure Machine learning cluster name")
    parser.add_argument("--cluster_size", type=str, help="Azure Machine learning cluster size")
    parser.add_argument("--cluster_region", type=str, help="Azure Machine learning cluster region")
    parser.add_argument("--min_instances", type=int, default=0)
    parser.add_argument("--max_instances", type=int, default=4)
    parser.add_argument("--idle_time_before_scale_down", type=int, default=120)
    parser.add_argument("--build_reference", type=str, help="Unique identifier for Azure DevOps pipeline run")
    parser.add_argument("--deploy_environment", type=str, help="execution and deployment environment. e.g. dev, prod, test")
    parser.add_argument("--experiment_name", type=str, help="Job execution experiment name")
    parser.add_argument("--display_name", type=str, help="Job execution run name")
    parser.add_argument("--ml_pipeline_name", type=str, help="name of pipeline")
    parser.add_argument("--wait_for_completion", type=str, help="determine if pipeline to wait for job completion")
    parser.add_argument("--environment_name", type=str, help="Azure Machine Learning Environment name for job execution")
    parser.add_argument("--env_base_image_name", type=str, help="Environment custom base image name")
    parser.add_argument("--conda_path", type=str, help="path to conda requirements file")
    parser.add_argument("--env_description", type=str, default="Environment created using Conda.")

    args = parser.parse_args()

    compute = get_compute(
        args.subscription_id,
        args.resource_group_name,
        args.workspace_name,
        args.cluster_name,
        args.cluster_size,
        args.cluster_region,
        args.min_instances,
        args.max_instances,
        args.idle_time_before_scale_down
    )

    environment = get_environment(
        args.subscription_id,
        args.resource_group_name,
        args.workspace_name,
        args.env_base_image_name,
        args.conda_path,
        args.environment_name,
        args.env_description
    )

    ml_pipeline_name = args.ml_pipeline_name
    display_name = args.display_name
    experiment_name = args.experiment_name
    deploy_environment = args.deploy_environment
    build_reference = args.build_reference

    pipeline_job = construct_pipeline(
        compute.name,
        environment.name
    )

    execute_pipeline(
        args.subscription_id,
        args.resource_group_name,
        args.workspace_name,
        args.experiment_name,
        pipeline_job,
        args.wait_for_completion)


if __name__ == "__main__":
    main()
