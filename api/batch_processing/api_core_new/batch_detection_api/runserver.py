# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

"""
Flask entry point file for the batch processing API.
"""

import json
import math
import os
import time
from datetime import datetime
from random import shuffle
from threading import Thread
import string
import urllib.parse
from time import sleep

from flask import Flask, request, make_response, jsonify
# from azure.storage.blob import BlockBlobService
# /ai4e_api_tools has been added to the PYTHONPATH, so we can reference those libraries directly.
from ai4e_app_insights_wrapper import AI4EAppInsights
from ai4e_service import APIService

# import api_config
# import orchestrator
# from orchestrator import get_task_status
# from sas_blob_utils import SasBlob  # file in this directory, not the ai4eutil repo one


print('Creating Application')
app = Flask(__name__)

# Use the AI4EAppInsights library to send log messages. NOT REQURIED
log = AI4EAppInsights()

# Use the APIService to executes your functions within a logging trace, supports long-running/async functions,
# handles SIGTERM signals from AKS, etc., and handles concurrent requests.
with app.app_context():
    ai4e_service = APIService(app, log)


# Get the configuration values from our Azure App Configuration instance






# Define a function for processing request data, if applicable.  This function loads data or files into
# a dictionary for access in your API function.  We pass this function as a parameter to your API setup.
def process_request_data(request):
    print('in process_request_data')
    return_values = {'data': None}
    try:
        # Attempt to load the body
        return_values['data'] = request.get_json()
    except:
        log.log_error('Unable to load the request data')   # Log to Application Insights
    return return_values

# Define a function that runs your model.  This could be in a library.
def run_model(taskId, body):
    print('Task {} in run_model'.format(taskId))

    # Update the task status, so the caller knows it has been accepted and is running.
    ai4e_service.api_task_manager.UpdateTaskStatus(taskId, 'running model')

    log.log_debug('Running model', taskId) # Log to Application Insights
    #INSERT_YOUR_MODEL_CALL_HERE
    sleep(10)  # replace with real code

    # start the monitoring thread
    monitoring_kwargs = {
        'task_id': taskId,
        'other_info': 16
    }
    print('Task {} about to start monitoring thread'.format(taskId))
    monitoring_thread = Thread(target=monitor_aml_job, kwargs=monitoring_kwargs)
    monitoring_thread.start()


def monitor_aml_job(**kwargs):
    task_id = kwargs['task_id']
    print('Task {} in monitoring function'.format(task_id))
    sleep(60)
    print('Task {} about to complete task'.format(task_id))
    ai4e_service.api_task_manager.CompleteTask(task_id, {'status': 'complete', 'other_info': 2})


# POST, long-running/async API endpoint example
@ai4e_service.api_async_func(
    api_path = '/example',
    methods = ['POST'],
    request_processing_function = process_request_data, # This is the data process function that you created above.
    maximum_concurrent_requests = 3, # If the number of requests exceed this limit, a 503 is returned to the caller.
    content_types = ['application/json'],
    content_max_length = 1000, # In bytes
    trace_name = 'post:my_long_running_funct')
def default_post(*args, **kwargs):

    # Since this is an async function, we need to keep the task updated.
    taskId = kwargs.get('taskId')
    log.log_debug('Started task', taskId) # Log to Application Insights

    print('In async endpoint, task id is {}'.format(taskId))

    # Get the data from the dictionary key that you assigned in your process_request_data function.
    request_json = kwargs.get('data')

    if not request_json:
        ai4e_service.api_task_manager.FailTask(taskId, 'Task failed - Body was empty or could not be parsed.')
        return -1

    # Run your model function
    run_model(taskId, request_json)

    # Once complete, ensure the status is updated.
    # log.log_debug('Completed task', taskId) # Log to Application Insights
    # Update the task with a completion event.



@ai4e_service.api_sync_func(
    api_path='/default_model_version/<string:caller_id>',
    methods=['GET'],
    maximum_concurrent_requests=10,
    trace_name='get:default_model_version')
def default_model_version(*args, **kwargs):
    return '4.1 testing'


@ai4e_service.api_sync_func(
    api_path='/supported_model_versions',
    methods=['GET'],
    maximum_concurrent_requests=100,
    trace_name='get:supported_model_versions')
def supported_model_versions(*args, **kwargs):
    return jsonify(['2', '3', '4.1'])


@ai4e_service.api_sync_func(api_path = '/echo/<string:text>', methods = ['GET'], maximum_concurrent_requests = 1000, trace_name = 'get:echo', kwargs = {'text'})
def echo(*args, **kwargs):
    return 'Echo: ' + kwargs['text']

if __name__ == '__main__':
    app.run()
