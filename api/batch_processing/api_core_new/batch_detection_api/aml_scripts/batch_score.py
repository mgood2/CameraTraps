# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

"""
Script ran by the ParallelRunStep in the AML workspace.

It receives a batch of file paths via the run() function, and returns a serialized object in
the eventual output file's `images` field:

```json
{
    "file": "path/from/base/dir/image1.jpg",
    "max_detection_conf": 0.926,
    "detections": [
        {
            "category": "1",
            "conf": 0.926,
            "bbox": [0.0, 0.2762, 0.1539, 0.2825],
            "classifications": [
                ["3", 0.901],
                ["1", 0.071],
                ["4", 0.025]
            ]
        },
        {
            "category": "1",
            "conf": 0.061,
            "bbox": [0.0451, 0.1849, 0.3642, 0.4636]
        }
    ]
}
```

File paths that do not end in ('.jpeg', '.jpg', '.png') are ignored - they will not have an entry in the
output list.

If an error occurs, serialized object of this form will be returned, where `error` will be a non-zero int:

```json
{
    "file": "path/from/base/dir/image1.jpg",
    "error": 1,
    "error_message": "string explaining the error, with the exception if available"
}
```

The `meta` field in each entry will be added by the API code, if needed.

Instructions for writing the batch scoring script:
https://docs.microsoft.com/en-us/azure/machine-learning/how-to-use-parallel-run-step#write-your-inference-script
"""
print('batch_score.py, start')

import argparse
import json
import urllib.parse

import azureml.core
from PIL import Image
from azureml.core.model import Model
from run_tf_detector import TFDetector

print('batch_score.py, using AML version {}'.format(azureml.core.__version__))


# lower case; must be tuple for endswith to take as arg
ACCEPTED_IMAGE_FILE_EXTENSIONS = ('.jpeg', '.jpg', '.png')


def init():
    global tf_detector, detection_threshold

    parser = argparse.ArgumentParser(description='Batch score images using an object detection model.')
    parser.add_argument('--request_id', dest='request_id', required=True)  # for logging only
    parser.add_argument('--model_name', dest='model_name', required=True)
    parser.add_argument('--detection_threshold', dest='detection_threshold', type=float, default=0.05)
    args, _ = parser.parse_known_args()

    print(f'init(), arguments parsed. request_id {args.request_id}, model_name {args.model_name}, ' 
          f'detection_threshold {args.detection_threshold}')

    detection_threshold = args.detection_threshold  # used in run()

    # get the model from the workspace
    model_path = Model.get_model_path(args.model_name)
    print(f'init(), model_path is {model_path}')
    tf_detector = TFDetector(model_path)
    print('init(), TFDetector initialized')


def run(mini_batch):
    """

    Args:
        mini_batch: a list of paths to potential image files, locally mounted on the compute target

    Returns:
        a list of strings, which are JSON serialized result object, that becomes an entry in the `images` field
            of the eventual API output file
    """
    result_list = []
    print(f'run(), starting with mini_batch of length {len(mini_batch)}.')

    for file_path in mini_batch:
        print(f'run(), file_path {file_path}')

        # ignore files that do not have the allowed extensions
        if not urllib.parse.urlparse(file_path).path.lower().endswith(ACCEPTED_IMAGE_FILE_EXTENSIONS):
            print('run(), skipped, file name extension not acceptable')
            continue

        # following image opening and mode checking code copied from visualization/visualization_utils.py

        # open the image using PIL
        try:
            image = Image.open(file_path)
            # print(f'run(), file_path is {file_path}, image size is {image.size}')
        except Exception as e:
            error_entry = {
                'file': file_path,
                'error': 1,
                'error_message': f'Image cannot be opened: {e}'
            }
            result_list.append(json.dumps(error_entry))
            continue

        # reject if image does not have a mode convertable to RGB
        if image.mode not in ('RGBA', 'RGB', 'L'):
            error_entry = {
                'file': file_path,
                'error': 2,
                'error_message': f'Image is in an unsupported mode {image.mode}'
            }
            result_list.append(json.dumps(error_entry))
            continue

        # convert image to RGB mode as needed
        if image.mode == 'RGBA' or image.mode == 'L':
            try:
                # PIL.Image.convert() returns a converted copy of this image
                image = image.convert(mode='RGB')
            except Exception as e:
                error_entry = {
                    'file': file_path,
                    'error': 3,
                    'error_message': f'Failed to convert image to RGB mode: {e}'
                }
                result_list.append(json.dumps(error_entry))
                continue

        # apply detector to image
        try:
            res = tf_detector.generate_detections_one_image(image, file_path, detection_threshold=detection_threshold)
        except Exception as e:
            error_entry = {
                'file': file_path,
                'error': 4,
                'error_message': f'Failed to apply detector to image: {e}'
            }
            result_list.append(json.dumps(error_entry))
            continue

        # serialize results, otherwise it will be saved with single quote marks and be difficult to parse
        result_list.append(json.dumps(res))

    # print something to logs
    print(f'run(), about to return result list of length {len(result_list)}.')

    return result_list
