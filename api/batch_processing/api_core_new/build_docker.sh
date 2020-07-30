#!/bin/bash

# these dependency files are outside of the Docker context, so cannot use the COPY action
# in the Dockerfile to copy them into the Docker image.

## main dependency
#cp ../../../detection/run_tf_detector.py batch_detection_api/aml_scripts/
#
## which depends on ct_utils and visualization_utils
#cp ../../../ct_utils.py batch_detection_api/aml_scripts/
#
#mkdir batch_detection_api/aml_scripts/visualization/
#cp ../../../visualization/visualization_utils.py batch_detection_api/aml_scripts/visualization/
#
## visualization_utils in turn depends on the following
#mkdir batch_detection_api/aml_scripts/data_management
#mkdir batch_detection_api/aml_scripts/data_management/annotations/
#cp ../../../data_management/annotations/annotation_constants.py batch_detection_api/aml_scripts/data_management/annotations/

# get the credentials from KeyVault, which will be set as environment variables in the Docker container
az login

SUBSCRIPTION=74d91980-e5b4-4fd9-adb6-263b8f90ec5b
KEY_VAULT_NAME=siyu-kv

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

# Modify the version and build numbers as needed in the IMAGE_NAME argument passed to this script
echo About to build image $1
# sudo docker build . -t $1
