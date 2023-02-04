# How to setup the repo

This template supports Azure ML as a platform for ML, and Azure DevOps as a platform for operationalization. Therefore, we assume that you already have an Azure ML Workspace as well as an Azure DevOps project in place, and all the code from the repository has been cloned into the DevOps project.

In order to setup the repository, you need to complete few steps.

**Step 1.** Create a service connection in Azure DevOps. You can use [this document](https://learn.microsoft.com/en-us/azure/devops/pipelines/library/service-endpoints?view=azure-devops&tabs=yaml) as a reference. Use Azure Resource Manager as a type of the service connection.

**Step 2.** Create a new variable group with the following variables:

- EXPERIMENT_BASE_NAME: an experiment base name. This parameter as well as two more parameters below we are using as a background to form unique names for experiments, runs and models. You can find a rule for the names in [this template](../devops/pipeline/templates/experiment_variables.yml). By default we are using the branch name as well as build id to form the names that helps us to differentiate experiments, runs and models working in a big team of data scientists and software engineers. The EXPERIMENT_TYPE variable from the template is hard coded in _dev_pipeline.yml files.
- DISPLAY_BASE_NAME: a run base name (see EXPERIMENT_BASE_NAME for details).
- MODEL_BASE_NAME: a model base name (see EXPERIMENT_BASE_NAME for details).
- AZURE_RM_SVC_CONNECTION: the service connection name from the previous step.
- WORKSPACE_NAME: an Azure ML workspace name.
- RESOURCE_GROUP: a resource group where Azure Ml Workspace is located.
- CLUSTER_NAME: an Azure ML compute cluster name to start jobs.
- CLUSTER_SIZE: a size of the cluster in Azure ML to start jobs.

Information about variable groups in Azure DevOps can be found in [this document](https://learn.microsoft.com/en-us/azure/devops/pipelines/library/variable-groups?view=azure-devops&tabs=classic).

**Step 3.** Create a *development* branch and make it as default one to make sure that all PRs should go towards to it. This template assumes that the team works at a *development* branch as a primary source for coding and improving the model quality. Later, you can implement Azure Pipeline that mode code from the *development* branch into qa/main or execute a release process right away. Release management is not in scope of this template.

**Step 4.** Create two Azure Pipelines. Both Azure Pipelines should be created based on existing YAML files. The first one is based on the [pr_to_dev_pipeline.yml](../devops/pipeline/pr_to_dev_pipeline.yml), and it helps to maintain code quality for all PRs including integration tests for the Azure ML experiment. Usually, we recommend to have a toy dataset for the integration tests to make sure that the Azure ML job can be completed fast enough - there is no a goal to check model quality and we just need to make sure that our job can be executed. The second Azure Pipeline is based on [ci_dev_pipeline.yml](../devops/pipeline/ci_dev_pipeline.yml) that should be executed automatically once new PR has been merged into the *development* branch. The main idea of this pipeline is to execute training on the full dataset to generate a model that can be a candidate for production. This Azure Pipeline should be extended based on the project's requirements. 

More details about how to create a basic Azure Pipeline can be found [here](https://learn.microsoft.com/en-us/azure/devops/pipelines/create-first-pipeline?view=azure-devops&tabs).

**Step 5.** Setup a policy for the *development* branch. At this stage we have an Azure Pipeline that should be executed on every PR to the *development* branch. At the same time successful completion of the build is not a requirement. So, it's important to add our PR build as a policy. Pay special attention that pr_to_dev_pipeline.yml](../devops/pipeline/pr_to_dev_pipeline.yml) has various paths in place. We are using these paths to limit number of runs if the current PR doesn't affect ML component (for example, PR modifies a documentation file). Therefore, setting up the policy you need to make sure that you are using the same set of paths in the *Path filter* field.

More details about how to create a policy can be found [here](https://learn.microsoft.com/en-us/azure/devops/repos/git/branch-policies?view=azure-devops&tabs=browser).

**Step 6. (Optional)** It's a common practice to execute training job on the full dataset once PR has been merged into the development branch. At the same time, the training process can take much time (many hours or even days) and Azure DevOps agent will not be able to let you know about the status due to timeout settings. So, it's very hard to implement a single CI Build that is waiting for a new model (training results) and execute other steps after that (model approval, model movement into qa environment, model deployment etc).

Azure ML provides a solution that allows us to implement a *server* task in Azure DevOps Build and wait for the result of the pipeline training job with no Azure DevOps agent holding. Thanks to that it's possible to wait for results any amount of time and execute all other steps right after completion of the Azure ML training job. As for now, the feature is in active development, but you can [visit this link](https://github.com/Azure/azure-mlops-automation) to check the status and find how to get access. This new Azure ML feature can be included in your CI Build thanks to the extension that Azure ML team built or you can use RestAPITask for a direct REST call. In this template we implemented both options, and you can pick any.

To activate option 1, you need to uncomment it in `ci_dev_pipeline.yml`, and you need to setup a new Azure Resource Manager service connection in AzureML scope and add its name into the variable group as **ML_SCOPE_SVC_CONNECTION**.

To activate option 2, you need to uncomment it in `ci_dev_pipeline.yml`, and you need to setup a new **Generic** service connection with **Server URL** parameter in the following format `https://{azure ml workspace location}.experiments.azureml.net/webhook/v1.0/` and add its name into the variable group as **AML_REST_CONNECTION**.

Now, you can create a PR and test the flow.

**Step 7. (Optional)** The default Azure ML pipeline used in this repository is built using hard-coded jobs, but optionally you may wish to implement a [component](https://learn.microsoft.com/en-us/azure/machine-learning/concept-component) based pipeline. Components are self contained pieces of code that can be reused across multiple pipelines - which can be useful in customers who have many different pipelines that share common tasks.

To review these components, explore the `mlops\nyc-taxi\components` folder, and the YAML within, which defines each component. In this use case, each component maps directly to one of the jobs in the default pipeline, and in the `mlops\nyc-taxi\pipeline_components.yml` pipeline, they are executed in the same order.

If you want to test out the component based pipeline, simply comment out the reference to `mlops\nyc-taxi\pipeline.yml` in the `ci_dev_pipeline.yml` and `pr_to_def_pipeline.yml` and replace it with `mlops\nyc-taxi\pipeline_components.yml`, then re-run your Azure Pipelines.

For more information about components, please see the official docs [here](https://learn.microsoft.com/en-us/azure/machine-learning/concept-component).