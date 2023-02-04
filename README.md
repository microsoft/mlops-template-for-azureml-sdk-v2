# MLOps Basic Template for Azure ML CLI v2

> **Note:**
> This is a repo that can be shared to our customers. This means it's NOT OK to include Microsoft confidential
> content. All discussions should be appropriate for a public audience.

## About this repo

The idea of this template is to provide a minimum number of scripts to implement development environment to train new models using Azure ML CLI v2 and Azure DevOps.

The template contains the following folders/files:

- devops: the folder contains Azure DevOps related files (yaml files to define Builds).
- docs: documentation.
- src: source code that is not related to Azure ML directly. Usually, there is data science related code.
- mlops: scripts that are related to Azure ML.
- mlops/nyc-taxi: a fake pipeline with some basic code.
- .amlignore: using this file we are removing all the folders and files that are not supposed to be in Azure ML compute.

The template contains the following documents:

- docs/how_to_setup.md: explain how to configure the template.

## How to use the repo

Information about how to setup the repo is in [the following document](./docs/how_to_setup.md).
