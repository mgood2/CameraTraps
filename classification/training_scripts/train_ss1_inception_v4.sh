#@IgnoreInspection BashAddShebang
# Adjust to your environment
DATASET_NAME=ss_season1
DATASET_DIR=/datadrive/camtrap/benchmark_20190904/classifier_tfrecords/ss1_cropped_tfrecords
TRAIN_DIR=/datadrive/camtrap/benchmark_20190904/classifier/ss1/train/log_$(date +"%Y-%m-%d_%H.%M.%S")_ss1_incv4
#TRAIN_DIR=./log/init_test/
CHECKPOINT_PATH=/datadrive/camtrap/benchmark_20190904/classifier/pretrained/inception_v4.ckpt


MODEL_NAME=inception_v4
CHECKPOINT_EXCLUDE=InceptionV4/AuxLogits,InceptionV4/Logits
NUM_GPUS=1

# 50k iters
python train_image_classifier.py \
    --train_dir=${TRAIN_DIR}/init \
    --dataset_dir=${DATASET_DIR} \
    --dataset_name=${DATASET_NAME} \
    --dataset_split_name=train \
    --model_name=${MODEL_NAME} \
    --checkpoint_path=${CHECKPOINT_PATH} \
    --checkpoint_exclude_scopes=${CHECKPOINT_EXCLUDE} \
    --trainable_scopes=${CHECKPOINT_EXCLUDE} \
    --max_number_of_steps=50000 \
    --batch_size=32 \
    --learning_rate=0.01 \
    --learning_rate_decay_type=fixed \
    --save_interval_secs=600 \
    --save_summaries_secs=600 \
    --log_every_n_steps=100 \
    --optimizer=rmsprop \
    --weight_decay=0.00004

# 1.5M iters
python train_image_classifier.py \
    --train_dir=${TRAIN_DIR}/all \
    --dataset_dir=${DATASET_DIR} \
    --dataset_name=${DATASET_NAME} \
    --dataset_split_name=train \
    --model_name=${MODEL_NAME} \
    --checkpoint_path=${TRAIN_DIR}/init \
    --max_number_of_steps=110000 \
    --batch_size=32 \
    --learning_rate=0.0045 \
    --learning_rate_decay_factor=0.94 \
    --num_epochs_per_decay=1 \
    --save_interval_secs=600 \
    --save_summaries_secs=600 \
    --log_every_n_steps=10 \
    --optimizer=rmsprop \
    --weight_decay=0.00004

