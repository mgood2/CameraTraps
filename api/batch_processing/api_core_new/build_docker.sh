#!/bin/bash

# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.


# these dependency files are outside of the Docker context, so cannot use the COPY action
# in the Dockerfile to copy them into the Docker image.

# main dependency
cp ../../../detection/run_tf_detector.py batch_detection_api/aml_scripts/

# which depends on ct_utils and visualization_utils
cp ../../../ct_utils.py batch_detection_api/aml_scripts/

mkdir batch_detection_api/aml_scripts/visualization/
cp ../../../visualization/visualization_utils.py batch_detection_api/aml_scripts/visualization/

# visualization_utils in turn depends on the following
mkdir batch_detection_api/aml_scripts/data_management
mkdir batch_detection_api/aml_scripts/data_management/annotations/
cp ../../../data_management/annotations/annotation_constants.py batch_detection_api/aml_scripts/data_management/annotations/

# Get the credentials from KeyVault
# The build-arg values will be in the Docker image's history, but since our images are stored in a private
# Azure Container Registry, only people with access to the ACR instance has access to the values
SUBSCRIPTION=74d91980-e5b4-4fd9-adb6-263b8f90ec5b
KEY_VAULT_NAME=siyu-kv

# A URL and a code to use for logging in on the browser will be displayed
echo Log in to your Azure account via the CLI...
az login

TENANT_ID=`az keyvault secret show --name camera-trap-tenant-id --subscription $SUBSCRIPTION --vault-name $KEY_VAULT_NAME --query value`
echo TENANT_ID read from KeyVault

APPLICATION_ID=`az keyvault secret show --name camera-trap-application-id --subscription $SUBSCRIPTION --vault-name $KEY_VAULT_NAME --query value`
echo APPLICATION_ID read from KeyVault

AZUREML_PASSWORD=`az keyvault secret show --name camera-trap-azureml-password --subscription $SUBSCRIPTION --vault-name $KEY_VAULT_NAME --query value`
echo AZUREML_PASSWORD read from KeyVault

# for AML workspace to store its outputs
STORAGE_ACCOUNT_NAME=`az keyvault secret show --name camera-trap-storage-account-name --subscription $SUBSCRIPTION --vault-name $KEY_VAULT_NAME --query value`
echo STORAGE_ACCOUNT_NAME read from KeyVault

STORAGE_ACCOUNT_KEY=`az keyvault secret show --name camera-trap-storage-account-key --subscription $SUBSCRIPTION --vault-name $KEY_VAULT_NAME --query value`
echo STORAGE_ACCOUNT_KEY read from KeyVault

# for App Configuration
APP_CONFIG_CONNECTION_STR=`az keyvault secret show --name camera-trap-app-config-connection-str --subscription $SUBSCRIPTION --vault-name $KEY_VAULT_NAME --query value`
echo APP_CONFIG_CONNECTION_STR read from KeyVault

# Modify the version and build numbers as needed in the IMAGE_NAME argument passed to this script
echo About to build image $1
sudo docker build . -t $1 --build-arg TENANT_ID=$TENANT_ID --build-arg APPLICATION_ID=$APPLICATION_ID --build-arg AZUREML_PASSWORD=$AZUREML_PASSWORD --build-arg STORAGE_ACCOUNT_NAME=$STORAGE_ACCOUNT_NAME --build-arg STORAGE_ACCOUNT_KEY=$STORAGE_ACCOUNT_KEY --build-arg APP_CONFIG_CONNECTION_STR=$APP_CONFIG_CONNECTION_STR
