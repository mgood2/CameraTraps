# Camera trap batch processing API developer readme


## Build

Navigate to the current directory `api/batch_processing/api_core`.

In `Dockerfile`, fill out the necessary credentials `AZUREML_PASSWORD`, `STORAGE_ACCOUNT_NAME`, `STORAGE_ACCOUNT_KEY` and `APP_CONFIGURATION_CONNECTION_STR`. The storage credentials are for the storage account used to store the output files.

Modify the Docker image tag `-t`:


```bash
export IMAGE_NAME=yasiyu.azurecr.io/camera-trap/3-detection-batch:1

sudo sh build_docker.sh IMAGE_NAME
```



If you need to debug the environment set up interactively, comment out the entry point line at the end of the Dockerfile, build the Docker image, and start it interactively:
```bash
sudo docker run -p 6011:1212 -it $IMAGE_NAME /bin/bash
```

And start the gunicorn server program manually:
```bash
gunicorn -b 0.0.0.0:1212 runserver:app
```

To upload the Docker image:
```bash
sudo az acr login --name name_of_registry

sudo docker push $IMAGE_NAME
```


## Deploy

Modify the port number to expose from this server VM (set to `6011` below). The second port number is the port exposed by the Docker container, specified in [Dockerfile](Dockerfile).

Can also specify a new path for the log file to append logs to. 

```bash
sudo docker run -p 6011:1212 $IMAGE_NAME |& tee -a /home/username/foldername/batch_api_logs/log_internal_20200707.txt

```

## Testing

